#ifndef LAYMAN_API_H
#define LAYMAN_API_H

#include "config.h"
#include "stringlist.h"

typedef struct LaymanAPI LaymanAPI;

typedef struct OverlayInfo
{
	char*		name;
	char*		text;
	char*		ownerEmail;
	char*		ownerName;
	char*		homepage;
	char*		description;
	char*		srcType;
	char*		quality;
	int		priority;
	StringList*	srcUris;
	int		official;
	int		supported;
} OverlayInfo;

LaymanAPI*	laymanAPICreate(BareConfig*, int, int);
int		laymanAPIIsRepo(LaymanAPI *l, const char* repo);
int		laymanAPIIsInstalled(LaymanAPI *l, const char* repo);
StringList*	laymanAPIGetAvailable(LaymanAPI*, int reload);
StringList*	laymanAPIGetInstalled(LaymanAPI*, int reload);
int		laymanAPISync(LaymanAPI* l, const char* overlay, int verbose);
int 		laymanAPIFetchRemoteList(LaymanAPI*);
int		laymanAPIGetInfosStr(LaymanAPI* l, StringList* overlays, OverlayInfo* results);
OverlayInfo*	laymanAPIGetInfoStr(LaymanAPI* l, const char* overlay);
int		laymanAPIGetAllInfos(LaymanAPI* l, StringList*, OverlayInfo*);
OverlayInfo*	laymanAPIGetAllInfo(LaymanAPI* l, const char*);
int		laymanAPIAddRepo(LaymanAPI* l, const char *repo);
int		laymanAPIAddRepos(LaymanAPI* l, StringList *repos);
int		laymanAPIDeleteRepo(LaymanAPI* l, const char *repo);
int		laymanAPIDeleteRepos(LaymanAPI* l, StringList *repos);
OverlayInfo*	laymanAPIGetInfo(LaymanAPI* l, const char* overlay);
void		laymanAPIFree(LaymanAPI*);
void		overlayInfoFree(OverlayInfo oi);

#endif
