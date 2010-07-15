#ifndef LAYMAN_API_H
#define LAYMAN_API_H

#include "config.h"
#include "stringlist.h"

typedef struct LaymanAPI LaymanAPI;

typedef enum OverlayType {Svn = 0, Git, Bzr} OverlayType;
typedef enum OverlayQuality {Experimental = 0, Stable, Testing} OverlayQuality;
typedef struct OverlayInfo
{
	char *text;
	/*char *name;
	char *source;
	char *contact;
	OverlayType type;
	int priority;
	OverlayQuality quality;
	char *description;
	char *link;
	char *feed;*/
	int official;
	int supported;
} OverlayInfo;


LaymanAPI*	laymanAPICreate(BareConfig*, int, int);
StringList*	laymanAPIGetAvailable(LaymanAPI*, int reload);
StringList*	laymanAPIGetInstalled(LaymanAPI*, int reload);
int		laymanAPISync(LaymanAPI* l, const char* overlay, int verbose);
int 		laymanAPIFetchRemoteList(LaymanAPI*);
OverlayInfo	*laymanAPIGetInfo(LaymanAPI* l, const char* overlay);
void		laymanAPIFree(LaymanAPI*);

#endif
