#include "SodTemplate.H"
#include <cstdio>


void print_header( const SodTemplate &tmplt )
{
   if ( ! tmplt.info ) return;

   const char *fmtd = "   %-21s=%10d\n";
   const char *fmtf = "   %-21s=%10f\n";
   const SodTemplate::Preamble &hdr = *tmplt.info;

   printf( fmtd, "template_obs", hdr.template_obs );
   printf( fmtd, "grouper_tag", hdr.grouper_tag );
   printf( fmtd, "grouper_version", hdr.grouper_version );
   printf( fmtd, "template_tag", hdr.template_tag );
   printf( fmtd, "template_sod_version", hdr.template_sod_version );
   printf( fmtd, "icolortmp", hdr.icolortmp );
   printf( fmtd, "ifieldtmp", hdr.ifieldtmp );
   printf( fmtd, "nccdtmp", hdr.nccdtmp );
   printf( fmtd, "ncrap0", hdr.ncrap0 );
   printf( fmtd, "nstot0", hdr.nstot0 );
   printf( fmtd, "ix_c", hdr.ix_c );
   printf( fmtd, "iy_c", hdr.iy_c );
   printf( fmtf, "amaj_st", hdr.amaj_st );
   printf( fmtf, "amin_st", hdr.amin_st );
   printf( fmtf, "tilt_st", hdr.tilt_st );
   printf( fmtf, "area_st", hdr.area_st );
   printf( fmtf, "airmasstmp", hdr.airmasstmp );
   printf( fmtf, "refangletmp", hdr.refangletmp );
   printf( fmtf, "colortermtmp", hdr.colortermtmp );
   printf( fmtd, "psf_star_count", hdr.psf_star_count );
   printf( fmtd, "template_star_count", tmplt.count->template_star_count );

   printf( "}\n" );
}

int main( int argc, char *argv[] )
{
  char *templateFileName = argv[1];

  SodTemplate tmplt;

  tmplt.open(templateFileName);

  print_header(tmplt);
}
