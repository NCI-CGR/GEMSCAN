#!/usr/bin/env python3

"""
The script merges calls from DeepVariant, HaplotypeCaller and Strelka2
"""

# at some point, stop using print statements to log and use an actual logging framework.

import argparse
import csv
import datetime
import re
import sys

# global variables:
# VCF structure (used instead of index numbers for readability)
chrom = 0
pos = 1
snpID = 2
ref = 3
alt = 4
qual = 5
filt = 6
info = 7
frmt = 8


############################################# Functions #############################################


def get_args():
    """Handle command line arguments (input and output file names)."""
    parser = argparse.ArgumentParser(
        description="Takes VCF file with samples that have been called by the three callers and returns a VCF file where the genotypes from each caller are combined."
    )
    parser.add_argument("infile", help="Input VCF file name")
    parser.add_argument("outfile", help="Output VCF file name")
    results = parser.parse_args()
    return results.infile, results.outfile


def check_file(fname):
    """Check that file can be read; exit with error message if not."""
    try:
        f = open(fname, "rb")
        f.close()
        return 0
    except IOError:
        print("ERROR: Could not read file", fname)
        return 1
        sys.exit()
    f.close()


def get_header(infile):
    """Extract header from VCF.
    Exit with error message if no header detected.
    """
    headerCheck = 1
    with open(infile, "r") as file:
        for line in csv.reader(file, delimiter="\t"):
            if "#CHROM" in line:
                headerCheck = vcf_check(line)
                return line
        if headerCheck == 1:
            print("ERROR: File must contain header row matching VCF specification")
            return 1
            sys.exit()


def vcf_check(line):
    """Rudimentary format check.
    Must have #CHROM-designated header row and >=2 genotype columns.
    Must have an 3X number of genotype columns (does not actually
    check pairing).
    """
    if (len(line) - 9) % 3 != 0 or len(line) < 12:
        print("ERROR: Unpaired sample names detected.  File must contain triple number of samples.")
        return 1
        sys.exit()
        # note that there should be (9 + 3 x no. of samples) number of columns
    else:
        return 0


def evaluate_variant_line(line, start1, end1, start2, end2, start3, end3):
    """For non-header lines, determines what needs to be done
    do merge the genotype information:
        1. Add set annotation (HC, DV, strelka2, HC-DV, HC-strelka2, DV-strelka2, HC-DV-strelka2) to INFO
        2. Removes empty genotypes for variants called by one caller
        3. Removes chr_pos_ref_alt from ID field for DV-only variants
        4. Integrates info for variants called by both
    """
    if (":DV_" in line[frmt]) and not (":HC_" in line[frmt]) and not (":strelka2_" in line[frmt]):
        line = add_set_tag("DV", line)
        line[filt] = "oneCaller"
        line = remove_empty_genotypes(line, start1, end1, start2, end2, start3, end3)
        line[snpID] = "."
        return line
    elif (":HC_" in line[frmt]) and not (":DV_" in line[frmt]) and not (":strelka2_" in line[frmt]):
        line = add_set_tag("HC", line)
        line[filt] = "oneCaller"
        line = remove_empty_genotypes(line, start1, end1, start2, end2, start3, end3)
        return line
    elif (":DV_" in line[frmt]) and (":HC_" in line[frmt]) and not (":strelka2_" in line[frmt]):
        line = add_set_tag("HC-DV", line)
        line[filt] = "twoCallers"
        line = combine_genotypes(line, start1, end1, start2, end2, start3, end3)
        line[snpID] = "."
        return line
    elif (":strelka2_" in line[frmt]) and not (":HC_" in line[frmt]) and not (":DV_" in line[frmt]):
        line = add_set_tag("strelka2", line)
        line[filt] = "oneCaller"
        line = remove_empty_genotypes(line, start1, end1, start2, end2, start3, end3)
        line[snpID] = "."
        return line
    elif (":strelka2_" in line[frmt]) and (":HC_" in line[frmt]) and not (":DV_" in line[frmt]):
        line = add_set_tag("HC-strelka2", line)
        line[filt] = "twoCallers"
        line = combine_genotypes(line, start1, end1, start2, end2, start3, end3)
        line[snpID] = "."
        return line
    elif (":strelka2_" in line[frmt]) and (":DV_" in line[frmt]) and not (":HC_" in line[frmt]):
        line = add_set_tag("DV-strelka2", line)
        line[filt] = "twoCallers"
        line = combine_genotypes(line, start1, end1, start2, end2, start3, end3)
        line[snpID] = "."
        return line
    elif (":strelka2_" in line[frmt]) and (":HC_" in line[frmt]) and (":DV_" in line[frmt]):
        line = add_set_tag("HC-DV-strelka2", line)
        line[filt] = "threeCallers"
        line = combine_genotypes(line, start1, end1, start2, end2, start3, end3)
        line[snpID] = "."
        return line
    else:
        print("ERROR: No caller annotation found in FORMAT field.")
        return 1
        sys.exit()


def find_genotype_indices(line):
    """Determines the start/stop point for genotype columns from the three callers.
    bcftools merge --force-samples results in a VCF with samples as so:
        chr pos ... sample1 sample2 2:sample1 2:sample2 3:sample1 3:sample2, where the first
        two columns are called with caller1 and the second two with caller2, and so on.
    This function determines the index numbers defining the ranges
    (assuming the columns are not inter-mingled, e.g. sample1 2:sample1 2:sample2 sample2).

    Bear in mind that python slicing [start:stop] gets items start to stop-1.
    Example: vcf with 6 genotype fields at indices 9-14: 0,1,...8,9,10,11,12,13,14
        see inline comments working through this example.
    """
    start1 = 9  # start1=9; index=9 field
    end3 = len(line)  # end2=15; index=15-1=14 field
    num_samples = int((end3 - 9) / 3)
    end1 = 9 + num_samples
    start2 = end1
    end2 = 9 + num_samples * 2
    start3 = end2
    return start1, end1, start2, end2, start3, end3


def add_set_tag(caller, line):
    """Add set (HC, DV, HC-DV, strelka2, HC-strelka2, DV-strelka2 and HC-DV-strelka2) to INFO fields."""
    line[info] = line[info] + ";set=" + caller
    return line


def remove_empty_genotypes(line, start1, end1, start2, end2, start3, end3):
    """For variants found by only one caller, remove empty (.:.:.) fields.
       If only DeepVariant has call, set dv_priority_GT to the DV GT
       Set all consensus GT to ./.
    """
    line[8] = line[8] + ":concensus_GT:dv_priority_GT"

    if any("0" in s for s in line[start1:end1]) or any("1" in s for s in line[start1:end1]):
        for i in range(start1, end1):
            line[i] = line[i] + ":" + "./." + ":" + "./."
        line = line[0:end1]
        return line
    elif any("0" in s for s in line[start2:end2]) or any("1" in s for s in line[start2:end2]):
        for i in range(start2, end2):
            s = line[i]
            geno = s.split(":")
            line[i] = line[i] + ":" + "./." + ":" + geno[0]
        line = line[0:9] + line[start2:end2]
        return line
    elif any("0" in s for s in line[start3:end3]) or any("1" in s for s in line[start3:end3]):
        for i in range(start3, end3):
            line[i] = line[i] + ":" + "./." + ":" + "./."
        line = line[0:9] + line[start3:end3]
        return line
    else:
        print("remove_empty_genotypes ERROR: All genotype fields are blank.")
        print(line)
        return 1
        sys.exit()


def flip_hets(gt):
    if gt == "1/0":
        gt = "0/1"
    return gt


def get_concensus_gt(gt1, gt2, gt3):  # In this order: HC, DV, strelka2
    """
    This function finds the consensus GT
    If all 3 callers have calls:
        and any of the two callers are concordant:  GT is set to that concordant GT;
        or none are concordant: GT is set to ./.
    If only 2 callers have calls:
        and they are concordant: GT is set to that concordant GT;
        and they are not concordant: GT is set to ./.
    Finally, If only one caller has call, it's set to ./.
    """
    if flip_hets(gt1) == flip_hets(gt2):
        concensus_gt = gt1
    elif flip_hets(gt2) == flip_hets(gt3):
        concensus_gt = gt2
    elif flip_hets(gt1) == flip_hets(gt3):
        concensus_gt = gt1
    else:
        concensus_gt = "./."
    return concensus_gt


def get_dv_priority_gt(gt1, gt2, gt3):  # In this order: HC, DV, strelka2
    """
    This function finds the GT that's from DV call when possible.
    If there's no DV call:
        and HC and strelka2 calls the same genotype, GT is set to that genotype
        otherwise GT is set to ./.
    """
    dv_priority_gt = "./."
    if gt2.count(".") == 0:
        dv_priority_gt = gt2
    elif flip_hets(gt1) == flip_hets(gt3):
        dv_priority_gt = gt1
    return dv_priority_gt


def combine_genotypes(line, start1, end1, start2, end2, start3, end3):
    """For variants found by only two callers, integrate genotype info.
    Variants called by both callers will look like this:
        sample1          2:sample1
        0/1:3:4,5:.:.:.  .:.:.:0/1:2:4,3
    We want the union of this information, e.g.:
        sample1
        0/1:3:4,5:0/1:2:4,3
    This function compares the three genotype fields sample1, 2:sample1 and 3:sample1,
    and anywhere there's a '.' in sample1, it updates it with non-'.'
    data from 2:sample1 or 3:sample1 if available.  This assumes that the VCF is well-formed,
    meaning each genotype column conforms equally to the FORMAT definition.

    This function also updates the GT column.
    If all 3 callers have calls:
        and any of the two callers are concordant:  GT is set to that concordant GT;
        or none are concordant: GT is set to ./.
    If only 2 callers have calls:
        and they are concordant: GT is set to that concordant GT;
        and they are not concordant: GT is set to ./.
    Finally, If only one caller has call, it's set to that GT
    """

    for x, y, z in zip(line[start1:end1], line[start2:end2], line[start3:end3]):
        geno1 = x.split(":")
        geno2 = y.split(":")
        geno3 = z.split(":")
        field = line.index(x)
        for i, g1 in enumerate(geno1):
            if i == 0:
                if (geno1[i] != geno2[i]) and (geno1[i] != geno3[i]) and (geno2[i] != geno3[i]):
                    geno1[i] = "./."
                elif geno2[i] == geno3[i]:
                    geno1[i] = geno2[i]
            if (geno1[i] == ".") and (geno2[i] != "."):
                geno1[i] = geno2[i]
            if (geno1[i] == ".") and (geno2[i] == ".") and (geno3[i] != "."):
                geno1[i] = geno3[i]
        line[field] = ":".join(geno1)
        # add GT
        concensus_gt = get_concensus_gt(geno1[0], geno2[0], geno3[0])

        # print ("for dv:" + geno1[0] + " " + geno2[0] + " " + geno3[0])
        dv_priority_gt = get_dv_priority_gt(geno1[0], geno2[0], geno3[0])
        # print ("dv_priority_gt:" + dv_priority_gt)

        line[field] = line[field] + ":" + concensus_gt + ":" + dv_priority_gt

    # add field to format
    line[start1 - 1] = line[start1 - 1] + ":concensus_GT:dv_priority_GT"

    return line[0:end1]


def add_headers(ts, ver, scriptName, cmdString):
    """Add metadata to the vcf
    To A) account for new INFO field and to B) document provenance.
    ###TODO: add reference info as well?
    """
    infoHeader = '##INFO=<ID=set,Number=.,Type=String,Description="Set of callers that identified a variant (HC, DV, strelka2, HC-DV, HC-strelka2, DV-strelka2, or HC-DV-strelka2 )">'
    filterHeaderOneCaller = (
        '##FILTER=<ID=oneCaller,Description="The variant was called by exactly one caller">'
    )
    filterHeaderTwoCallers = (
        '##FILTER=<ID=twoCallers,Description="The variant was called by exactly two callers">'
    )
    filterHeaderThreeCallers = (
        '##FILTER=<ID=threeCallers,Description="The variant was called by all three callers">'
    )
    formatHeaderConcensusGT = (
        '##FORMAT=<ID=concensus_GT,Number=1,Type=String,Description="Genotype">'
    )
    formatHeaderDVPriorityGT = (
        '##FORMAT=<ID=dv_priority_GT,Number=1,Type=String,Description="Genotype">'
    )
    prov1 = (
        "##"
        + scriptName
        + "_Version="
        + ver
        + ", Union of HC, DV and strelka2 genotype data, "
        + ts
    )
    prov2 = "##" + scriptName + "_Command=" + cmdString
    return [
        filterHeaderOneCaller,
        filterHeaderTwoCallers,
        filterHeaderThreeCallers,
        infoHeader,
        formatHeaderConcensusGT,
        formatHeaderDVPriorityGT,
        prov1,
        prov2,
    ]


#####################################################################################################


if __name__ == "__main__":
    ts = str(datetime.datetime.now())
    ver = "someversion"  # https://stackoverflow.com/questions/5581722/how-can-i-rewrite-python-version-with-git
    scriptName = sys.argv[0]
    cmdString = " ".join(sys.argv)
    infile, outfile = get_args()
    check_file(infile)
    headerLine = get_header(infile)
    start1, end1, start2, end2, start3, end3 = find_genotype_indices(headerLine)
    with open(infile, "r") as file, open(outfile, "w") as out:
        for line in csv.reader(file, delimiter="\t"):
            if re.search(r"#", line[chrom]) is None:
                line = evaluate_variant_line(line, start1, end1, start2, end2, start3, end3)
                out.write("\t".join(line) + "\n")
            elif "#CHROM" in line:
                out.write("\n".join(add_headers(ts, ver, scriptName, cmdString)) + "\n")
                out.write("\t".join(line[0:start2]) + "\n")
            else:
                out.write("\t".join(line) + "\n")
