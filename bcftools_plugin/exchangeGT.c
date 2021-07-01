/*  exchangeGT.c -- change GT from one of the GT fields 

    Copyright (C) 2014-2016 Genome Research Ltd.

    Author: Wendy Wong, modified from Petr Danecek's tag2tag plugin <pd3@sanger.ac.uk>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.  */

#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <math.h>
#include <inttypes.h>
#include <htslib/hts.h>
#include <htslib/vcf.h>
#include "bcftools.h"

#define DV_GT 1
#define HC_GT 2     
#define strelka2_GT 3
#define dv_priority_GT 4
#define concensus_GT 5

static int gt_mode = 0;
static bcf_hdr_t *in_hdr, *out_hdr;
static char **farr = NULL; 
static int32_t *iarr = NULL;
static int mfarr = 0, miarr = 0;

char *src_tag = "concensus_GT";

const char *about(void)
{
    return "Change the main GT to one of the GT fields user specified.\n";
}

const char *usage(void)
{
    return 
        "\n"
        "About: Use one of the GT fields, such as DV_GT, HC_GT and strelka2_GT, dv_priority_GT or concensus_GT as the main GT.\n"
        "If the source GT field is not present the variant will be filtered out in the output VCF\n"
        "Usage: bcftools +exchangeGT [General Options] -- [Plugin Options]\n"
        "Options:\n"
        "   run \"bcftools plugin\" for a list of common options\n"
        "\n"
        "Plugin options:\n"
        "       --DV           convert FORMAT/DV_GT to FORMAT/GT\n"
        "       --HC           convert FORMAT/HC_GT to FORMAT/GT\n"
        "       --strelka2     convert FORMAT/strelka2_GT to FORMAT/GT\n"
        "       --dv_priority  convert FORMAT/dv_priority_GT to FORMAT/GT\n"
        "       --concensus    convert FORMAT/concensus_GT to FORMAT/GT\n"
        "\n"
        "Example:\n"
        "   bcftools +exchangeGT in.vcf --  --DV\n"
        "\n";
}


static void init_header(bcf_hdr_t *hdr, const char *ori, int ori_type, const char *new_hdr_line)
{
    if ( ori )
        bcf_hdr_remove(hdr,ori_type,ori);

    bcf_hdr_append(hdr, new_hdr_line);
}

int init(int argc, char **argv, bcf_hdr_t *in, bcf_hdr_t *out)
{
    static struct option loptions[] =
    {
        {"DV",no_argument,NULL,1},
        {"HC",no_argument,NULL,2},
        {"strelka2",no_argument,NULL,3},
        {"dv_priority",no_argument,NULL,4},
        {"concensus",no_argument,NULL,5},
        {NULL,0,NULL,0}
    };
    int c;
   
    while ((c = getopt_long(argc, argv, "?hrt:",loptions,NULL)) >= 0)
    {
        switch (c) 
        {
            case  1 : src_tag = "DV_GT"; gt_mode = DV_GT; break;
            case  2 : src_tag = "HC_GT"; gt_mode = HC_GT; break;
            case  3 : src_tag = "strelka2_GT"; gt_mode = strelka2_GT; break;
            case  4 : src_tag = "dv_priority_GT"; gt_mode = dv_priority_GT; break;
            case  5 : src_tag = "concensus_GT"; gt_mode = concensus_GT; break;          
            case 'h':
            case '?':
            default: error("%s", usage()); break;
        }
    }
    
    in_hdr  = in;
    out_hdr = out;
    
    init_header(out_hdr,NULL, BCF_HL_FMT,"##FORMAT=<ID=GT,Number=1,Type=String,Description=\"Genotype\">");
    
    int tag_id;
    if ( (tag_id=bcf_hdr_id2int(in_hdr,BCF_DT_ID,src_tag))<0 || !bcf_hdr_idinfo_exists(in_hdr,BCF_HL_FMT,tag_id) )
        error("The source tag does not exist: %s\n", src_tag);

    return 0;
}

bcf1_t *process(bcf1_t *rec)
{
    int i, n;
    char* src_tag = "concensus_GT";
    
    switch(gt_mode){
        case  DV_GT : src_tag = "DV_GT";  break;
        case  HC_GT : src_tag = "HC_GT"; break;
        case  strelka2_GT : src_tag = "strelka2_GT";  break;
        case  dv_priority_GT : src_tag = "dv_priority_GT";  break;
        case  concensus_GT : src_tag = "concensus_GT";  break;          
    }
    
    n = bcf_get_format_string(in_hdr,rec,src_tag,&farr,&mfarr);
    
    if ( n<=0 ) return NULL; //rec;
    
    int nsmpl = bcf_hdr_nsamples(in_hdr);
   
    hts_expand(int32_t,n*2,miarr,iarr);
    
    for (i=0; i<nsmpl; i++) {
        iarr[2*i] = iarr[2*i+1] = bcf_gt_missing;
         
        if (!farr[i]) {continue;}

       if (strcmp (farr[i], "0/0") == 0) {
           iarr[2*i]   = bcf_gt_unphased(0);
           iarr[2*i+1] = bcf_gt_unphased(0);
       } else if (strcmp (farr[i], "0/1") == 0 || strcmp (farr[i], "1/0") == 0) {
           iarr[2*i]   = bcf_gt_unphased(0);
           iarr[2*i+1] = bcf_gt_unphased(1);
       } else if (strcmp (farr[i], "1/1") == 0 ) {
            iarr[2*i]   = bcf_gt_unphased(1);
            iarr[2*i+1] = bcf_gt_unphased(1);
       } 
        
    }
    
    bcf_update_genotypes(out_hdr,rec,iarr,nsmpl*2);    
    
    return rec;
}

void destroy(void)
{
    free(farr);
    free(iarr);
}


