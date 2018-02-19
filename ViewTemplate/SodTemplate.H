/* written by John Doug Reynolds, April 1996 */
/* Modified by Tim Axelrod, Feb 2018 to work on a Linux system, standalone */

#ifndef _SodTemplate_h
#define _SodTemplate_h
#include <stdint.h>
#include <endian.h>
#include <string.h>
#include <cstddef>
#include <fcntl.h>
/*
 * Read-only access to SoDOPHOT small format templates
 * find() returns a record number suitable for use with operator[]
 * find() returns -1 on error and operator[] returns 0 on error
 */

class SodTemplate  {
private:
   int			size;
   char			*map;
   int			initialize( void );

public:
   struct Preamble {
      uint32_t _start1;
      uint32_t		template_obs;		// template image obs number
      uint32_t		grouper_tag;		// Grouper run date-tag
      uint32_t		grouper_version;	// TR Grouper version number
      uint32_t		template_tag;		// tmpl reduction run date-tag
      uint32_t		template_sod_version;	// TR Sod source version used
      uint32_t _end1;
      uint32_t _start2;
      uint32_t		icolortmp, ifieldtmp, nccdtmp;
      uint32_t		ncrap0, nstot0, ix_c, iy_c;
      uint32_t		spare1[2];
      float		amaj_st, amin_st, tilt_st, area_st; 
      float		airmasstmp, refangletmp, colortermtmp;
      float		spare2[3];
      uint32_t _end2;
      uint32_t _start3;
      uint32_t		psf_star_count;		// number of PSF stars
      uint32_t _end3;
      uint32_t _start4;
   };
   struct PsfStarId {
      uint16_t	tile;
      uint16_t	seqn;
   };
   struct StarCount {
      uint32_t _end4;
      uint32_t _start5;
      uint32_t		template_star_count;	// number of stars in template
      uint32_t _end5;
   };
   struct Star {
      unsigned short	tile;
      unsigned short	seqn;
      short		mag;			// Sod mag in this color
      short		flag;			// Sod TR flag
      short		other_mag;		// Sod mag in other color
      short		other_flag;		// Sod TR flag in other color
      short		coord_flag;		// Sod TR "pixel coord" flag
      short		x_pix;			// x coord, modulo 512
      short		y_pix;			// y coord, modulo 512
   };
   struct StarGroup {
      uint32_t _start;
      Star		star[100];
      uint32_t _end;
   };

   Preamble		*info;		// pointers into memory map
   PsfStarId		*psfid;
   StarCount		*count;
   StarGroup		*group;

   char*		filename;	// template file name
   int			npsf;		// = info->psf_star_count
   int			nstar;		// = count->template_star_count

		SodTemplate( void );
		~SodTemplate( void );

   int		open( const char *fname );
   void		close( void );

   Star*	operator [] ( int index ) const;
   int		find( ushort tile, ushort seqn ) const;
};

#endif

