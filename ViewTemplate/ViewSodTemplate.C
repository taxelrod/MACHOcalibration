/* written by John Doug Reynolds, January 1997 */

#include "SodTemplate.H"
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <cstdio>

enum FindMode { FindHeader, FindPSF, FindStarid, FindRecord };
enum DispMode { DispStarid, DispIndex, DispRecord, DispTableFmt };

class StarList {
public:
   struct StarId {
      unsigned short	tile;
      unsigned short	seqn;
   };
   	StarList( void );
   	~StarList( void );
   int	add( unsigned short tile, unsigned short seqn );
   int	dump( void );

private:
   struct StarId	*list;
   int			max, next;
};

int usage( const char *app )
{
   fprintf( stderr, "\
usage: %s [-d <directory>] [-f <field>] [-c [-]<chunk>]\n\
                       [-h] [-e|w] [-r|b] [-o starid | index | record]\n\
                       [hdr | psf | <starid> | <recno>]\n\n\
   Prints selected records from the SodTemplate database.  The field must\n\
   be specified, except when searching for a star by its id.\n\n\
       -d <dir>       Use dir instead of MACHOACTIVE from the environment.\n\
       -f <field>     Specify the (positive) field number.  No default.\n\
       -c [-]<chunk>  Specify the chunk number, with minus to indicate the\n\
                      East layout.  The default is all chunks.\n\
       -h             Print this usage statement.\n\
       -e|w           Select East or West pier-side.  The default is both.\n\
       -r|b           Select Red or Blue focal-plane.  The default is both.\n\
       -o <format>    Specify output format: starid for starid only, index\n\
                      for starid and index, record for database contents.\n\
                      The default is record.\n\
       hdr            Print the template headers.  Default action.\n\
       psf            Select the PSF stars.\n\
       <starid>       Select a star by <field>.<tile>.<sequence>.\n\
       <recno>        Select a star by record number.\n\
\n"
	    , app );

   return 1;
}

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

void print( enum DispMode disp_mode
	    , const SodTemplate::Star &star,  int recno )
{
   switch ( disp_mode ) {
   case DispStarid:
      printf( "%d.%d\n",  star.tile, star.seqn );
      break;
   case DispIndex:
      printf( "%d.%d record %d\n"
	      , star.tile, star.seqn, recno );
      break;
   case DispRecord:
      {
	 const char *fmt = "   %-11s=%7d\n";

	 printf( "record %d {\n", recno );

	 printf( fmt, "tile", star.tile );
	 printf( fmt, "seqn", star.seqn );
	 printf( fmt, "mag", star.mag );
	 printf( fmt, "flag", star.flag );
	 printf( fmt, "other_mag", star.other_mag );
	 printf( fmt, "other_flag", star.other_flag );
	 printf( fmt, "coord_flag", star.coord_flag );
	 printf( fmt, "x_pix", star.x_pix );
	 printf( fmt, "y_pix", star.y_pix );

	 printf( "}\n" );
      }
      break;
   case DispTableFmt:
     {
       printf( "%d %d %d %d %d %d\n", star.tile, star.seqn, star.mag, star.flag, star.other_mag, star.other_flag);
     }
     break;
   }
}

void print( enum DispMode disp_mode, const SodTemplate &tmplt
	    , unsigned short tile, unsigned short seqn )
{
   int recno = tmplt.find( tile, seqn );
   if ( recno != -1 ) print( disp_mode, *tmplt[recno],  recno );
}

int main( int argc, char *argv[] )
{
   int i, j;

   // parse the command line

   enum FindMode find_mode = FindHeader;
   enum DispMode disp_mode = DispRecord;
   unsigned short tile, seqn;
   int recno;

   char *templateFileName = argv[1];
   SodTemplate tmplt;
   tmplt.open(templateFileName);
   
   for ( i = 2; i < argc; ++i ) {
      if ( strcmp( argv[i], "-o" ) == 0 && i + 1 < argc ) {
	 char *arg = argv[++i];
	 if ( strcmp( arg, "starid" ) == 0 ) disp_mode = DispStarid;
	 else if ( strcmp( arg, "index" ) == 0 ) disp_mode = DispIndex;
	 else if ( strcmp( arg, "record" ) == 0 ) disp_mode = DispRecord;
	 else return usage( argv[0] );
      }
      else if ( strcmp( argv[i], "hdr" ) == 0 ) {
	 find_mode = FindHeader;
      }
      else if ( strcmp( argv[i], "psf" ) == 0 ) {
	 find_mode = FindPSF;
	 disp_mode = DispTableFmt;
      }
      else if ( sscanf(argv[i],"%hu.%hu",&tile,&seqn) == 3 && j > 0 ) {
	 find_mode = FindStarid;
      }
      else if ( sscanf( argv[i], "%d", &recno ) == 1 && recno >= 0 ) {
	 find_mode = FindRecord;
      }
      else return usage( argv[0] );
   }

   // process the template, tmplt

   StarList list;

   switch ( find_mode ) {
   case FindHeader:
     print_header( tmplt );
     break;
   case FindPSF:
     if ( disp_mode == DispStarid ) {
       for ( int k = 0; k < tmplt.npsf; ++k ) {
	 SodTemplate::PsfStarId &id = tmplt.psfid[k];
	 list.add( id.tile, id.seqn );
       }
     }
     else {
       printf("%d\n", tmplt.info->template_obs);
       for ( int k = 0; k < tmplt.npsf; ++k ) {
	 SodTemplate::PsfStarId &id = tmplt.psfid[k];
	 print( disp_mode, tmplt
		, id.tile, id.seqn );
       }
     }
     break;
   case FindStarid:
     if ( (recno=tmplt.find(tile,seqn)) != -1 ) {
       print( disp_mode, *tmplt[recno],  recno );
       if ( disp_mode == DispStarid ) return 0;
     }
     break;
   case FindRecord:
     if ( recno < tmplt.nstar )
       print( disp_mode, *tmplt[recno],  recno );
     break;
   }

   if ( find_mode == FindPSF && disp_mode == DispStarid ) list.dump();

   return 0;
}

/* --- StarList methods ---------------------------------------------------- */

StarList::StarList( void )
{
   list = 0;
   max = next = 0;
}

StarList::~StarList( void )
{
   if ( list ) delete [] list;
}

int	StarList::add( unsigned short tile, unsigned short seqn )
{
   if ( next >= max ) {
      int max1 = next + 12800;
      struct StarId *list1 = new StarId [ max1 ];
      if ( ! list1 ) return 1;
      if ( list ) {
	 memcpy( list1, list, next * sizeof(StarId) );
	 delete [] list;
      }
      list = list1;
      max = max1;
   }

   struct StarId &s = list[next++];

   s.tile = tile;
   s.seqn = seqn;

   return 0;
}

int	staridcompare( const void *v0, const void *v1 )
{
   const StarList::StarId &a = *((const StarList::StarId*) v0);
   const StarList::StarId &b = *((const StarList::StarId*) v1);

   if ( a.tile == b.tile )
     return a.seqn - b.seqn;
   else
     return a.tile - b.tile;

}

int	StarList::dump( void )
{
   if ( next < 1 ) return 0;

   qsort( list, next, sizeof(StarId), staridcompare );

   struct StarId invalid = { 0, 0 }, *last = &invalid;
   for ( int i = 0; i < next; ++i )
      if ( memcmp( &list[i], last, sizeof(StarId) ) ) {
	 last = &list[i];
	 printf( "%d.%d\n",  last->tile, last->seqn );
      }

   return 0;
}
