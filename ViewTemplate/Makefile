# written by John Doug Reynolds, May 1996

HDR		= SodTemplate.H

SRC		= SodTemplate.C

OBJS		= SodTemplate.o ViewSodTemplate.o

APP		= ViewSodTemplate

CCFLAGS		+= ${INCLUDE} -fpermissive

CCC             = g++

#------------------------------------------------------------------------------



#------------------------------------------------------------------------------

${APP} : ${OBJS}
	${CCC} -g -o ${APP} ${OBJS}

${OBJS} : ${HDR}

.SUFFIXES: .C .o

.c.o:
	gcc -c ${CFLAGS} $<

.C.o:
	${CCC} -g -c ${CCFLAGS} $<
