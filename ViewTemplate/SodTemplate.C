/* written by John Doug Reynolds, April 1996 */

#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include "SodTemplate.H"

SodTemplate::SodTemplate( void )
{
   map = 0;
   filename = 0;
   close();
}

SodTemplate::~SodTemplate( void )
{
   close();
}

void	SodTemplate::close( void )
{
   if ( map ) munmap( map, size );
   delete [] filename;
   map = 0;
   info = 0;
   psfid = 0;
   count = 0;
   group = 0;
   filename = 0;
   npsf = 0;
   nstar = 0;
}


int	SodTemplate::open( const char *fname )
{
   close();
   if ( !fname ) return -1;
   filename = new char [ strlen(fname) + 1 ];
   strcpy( filename, fname );
   return initialize();
}

int	SodTemplate::initialize( void )
{
   struct stat statbuf;
   if ( stat( filename, &statbuf ) ) return -1;
   size = (int) statbuf.st_size;
   int fd = ::open( filename, O_RDONLY );
   if ( fd == -1 ) return -1;
   map = mmap( NULL, size, PROT_WRITE, MAP_PRIVATE, fd, 0 );
   if ( map == (char*) -1 ) return -1;
   
   info = (Preamble*) map;
   // Convert Preamble from original big-endian to little-endian.  Preamble is all 32 bit quantities
   for (uint32_t *x = (uint32_t *)info; x < (uint32_t *)info + sizeof(Preamble)/sizeof(uint32_t); x++) {
     *x = be32toh(*x);
   }
   
   npsf = info->psf_star_count;
   psfid = (PsfStarId*) ( map + sizeof(Preamble) );
   // Convert psfid from original big-endian to little-endian. PsfStarId array is all 16 bit quantities
   for (int n = 0; n < npsf; n++) {
     PsfStarId *p = psfid + n;
     p->tile = be16toh(p->tile);
     p->seqn = be16toh(p->seqn);   
   }
   
   count = (StarCount*) ( psfid + npsf );
   // Convert endian for nstar
   count->template_star_count = be32toh(count->template_star_count);
   nstar = count->template_star_count;
   
   group = (StarGroup*) ( (char*) count + sizeof(StarCount) );
   // Convert endian for all Stars in all StarGroups

   int ngroup = nstar/100;
   if ( nstar%100 != 0) ngroup++;
   
   for (int n = 0; n < ngroup; n++) {
     StarGroup *sg = group + n;
     for (int i = 0; i < 100; i++) {
       Star *s = sg->star + i;
       for (uint16_t *x = (uint16_t *)s; x < (uint16_t *)s + sizeof(Star)/sizeof(uint16_t); x++) {
	 *x = be16toh(*x);
       }
     }
   }
   return 0;
}

SodTemplate::Star*	SodTemplate::operator [] ( int index ) const
{
   if ( !map  ||  index < 0  ||  index >= nstar ) return 0;
   return &group[index/100].star[index%100];
}

int	SodTemplate::find( ushort tile, ushort seqn ) const
{
   if ( !map ) return -1;
   for ( int g = 0 ;; ++g ) {
      long max = nstar - 100 * g;
      if ( max <= 0 ) return -1;
      if ( max > 100 ) max = 100;

      Star *star = group[g].star;
      for ( int s = 0; s < max; ++s, ++star )
	 if ( star->seqn == seqn  &&  star->tile == tile ) return 100 * g + s;
   }
}
