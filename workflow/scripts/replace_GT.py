#!/usr/bin/env python3

"""
This script replaces GT with the user select GT field, choices are:
HC_GT, DV_GT, strelka2_GT, concensus_GT, dv_priority_GT
It requires cyvcf2
"""

import argparse
import os.path

import numpy as np
from cyvcf2 import VCF, Writer


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputVCF", "-i", required=True)
    parser.add_argument("--outputVCF", "-o", required=True)
    parser.add_argument(
        "--gtTag",
        "-v",
        choices=["HC_GT", "DV_GT", "strelka2_GT", "concensus_GT", "dv_priority_GT"],
        required=True,
    )
    return parser


def replace_gt(variant, gtTag):
    """
  The input VCF from the GermlineVariantCallerV4 is almost majority voting except that it allows calls
  from only one caller to go through, this function replaces GT with one of the GT fields
  """

    print(type(variant))

    # convert back to a string.
    print(str(variant))

    print(variant.genotypes)
    # variant.genotypes = [[1, 1, True], [0, 0, False]]
    # print (variant.genotypes)

    print(variant.gt_types)  # gt_types is array of 0,1,2,3==HOM_REF, HET, UNKNOWN, HOM_ALT

    new_GTs = variant.format(gtTag)
    print(new_GTs)

    print(variant.format("GT"))

    print("len:" + str(len(variant.genotypes)))

    vcf_line = str(variant)
    vcf_fields = split("\t", vcf_line)

    for i in range(len(variant.genotypes)):
        sample = vcf_fields[i + 8]
        sample_fields[0] = new_GTs

    for i in range(len(variant.genotypes)):
        curr_GT = "./."
        if (
            HC_GT is not None and DV_GT is not None and strelka2_GT is not None
        ):  # all 3 callers present
            if HC_GT[i] == DV_GT[i] or HC_GT[i] == strelka2_GT[i]:
                curr_GT = HC_GT[i]
            elif DV_GT[i] == strelka2_GT[i]:
                curr_GT = DV_GT[i]
        if HC_GT is not None and DV_GT is not None and strelka2_GT is None:  # Strelka no call
            if HC_GT[i] == DV_GT[i]:
                curr_GT = HC_GT[i]
        if HC_GT is None and DV_GT is not None and strelka2_GT is not None:  # HC no call
            if strelka2_GT[i] == DV_GT[i]:
                curr_GT = strelka2_GT[i]
        if HC_GT is not None and DV_GT is None and strelka2_GT is not None:  # DV no call
            if HC_GT[i] == strelka2_GT[i]:
                curr_GT = HC_GT[i]
        # modify the genotype call
        # variant.genotypes[i] = [1, 1, True]
        variant.gt_types[i] = 3

    # variant.format['test'] = "sdfs"

    print("updated:")
    print(variant.genotypes)

    print(variant.format("GT"))

    print(str(variant))

    return variant


def deepvariant_priority_voting(record):
    """
  Since DeepVariant generally has good performance we implement this option to choose DeepVarint calls
  above the other two. And if DeepVariant calls are not present, we require the genotype calls from the other two
  callers to be consistent
  """


def main(args=None):
    parser = get_parser()
    args = parser.parse_args(args)
    print(args)

    # exit if input file not found
    input_vcf = args.inputVCF
    if not os.path.isfile(input_vcf):
        print("File " + input_vcf + " does not exist!")
        sys.exit()

    vcf = VCF(input_vcf, strict_gt=True)

    # writing output vcf
    vcf_writer = Writer(args.outputVCF, vcf)

    for variant in vcf:
        if args.voting == "majority":
            updated_variant = majority_voting(variant)
            print("here:")
            print(str(updated_variant))
            break

    vcf_writer.close()
    vcf.close()


if __name__ == "__main__":
    main()
