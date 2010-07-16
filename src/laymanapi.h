#ifndef LAYMAN_API_H
#define LAYMAN_API_H

#include "config.h"
#include "stringlist.h"

typedef struct LaymanAPI LaymanAPI;

typedef struct OverlayInfo
{
	char *name;
	char *text;
	int official;
	int supported;
} OverlayInfo;

LaymanAPI*	laymanAPICreate(BareConfig*, int, int);
StringList*	laymanAPIGetAvailable(LaymanAPI*, int reload);
StringList*	laymanAPIGetInstalled(LaymanAPI*, int reload);
int		laymanAPISync(LaymanAPI* l, const char* overlay, int verbose);
int 		laymanAPIFetchRemoteList(LaymanAPI*);
int		laymanAPIGetInfoList(LaymanAPI* l, StringList* overlays, OverlayInfo* results);
int		laymanAPIAddRepo(LaymanAPI* l, StringList *repos);
int		laymanAPIDeleteRepo(LaymanAPI* l, StringList *repos);
OverlayInfo*	laymanAPIGetInfo(LaymanAPI* l, const char* overlay);
void		laymanAPIFree(LaymanAPI*);

#endif
