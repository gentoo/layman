#ifndef LAYMAN_API_H
#define LAYMAN_API_H

#include "config.h"
#include "stringlist.h"

typedef struct LaymanAPI LaymanAPI;

typedef enum OverlayType {Svn = 0, Git, Bzr} OverlayType;
typedef enum OverlayQuality {Experimental = 0, Stable, Testing} OverlayQuality;
typedef struct OverlayInfo
{
	char *name;
	char *source;
	char *contact;
	OverlayType type;
	int priority;
	OverlayQuality quality;
	char *description;
	char *link;
	char *feed;
	int official;
	int supported;
} OverlayInfo;


LaymanAPI*	laymanAPICreate(BareConfig*, int, int);
StringList*	laymanAPIGetAvailable(LaymanAPI*);
StringList*	laymanAPIGetInstalled(LaymanAPI*);

/*
 * The Python API returns a list of warnings/sucesses/errors
 * In here, a boolean value is returned.
 * Warnings can be retreived with
 * 	laymanAPIWarnings()
 * 	laymanAPIErrors()
 * As there's only one argument here, there's need to have success results.
 *
 * The reason it's done this way is that the Python way of doing things is not the same as the Python way.
 *
 * FIXME:is it a good idea to have different APIs for different languages ?
 */
int 		laymanAPISync(LaymanAPI*, const char*);
int 		laymanAPIFetchRemoteList(LaymanAPI*);
const char*	laymanAPIGetInfo(LaymanAPI*, const char*);

void laymanAPIFree(LaymanAPI*);

#endif
