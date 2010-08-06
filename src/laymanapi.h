#ifndef LAYMAN_API_H
#define LAYMAN_API_H

#include "config.h"
#include "stringlist.h"

typedef struct LaymanAPI LaymanAPI;

/**
 * Contains all information for an overlay
 */
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

/**
 * Creates a LaymanAPI object that must be used in all function in this file.
 *
 * \param config a BareConfig object that contains all configuration options. If NULL, the default configuration will be used.
 * \param report_error if True, errors reporting on stdout will be activated.
 * \param output ?
 * \return a new instance of the LaymanAPI class, to be freed with laymanAPIFree()
 */
LaymanAPI*	laymanAPICreate(BareConfig* config, int report_error, int output);

int		laymanAPIIsRepo(LaymanAPI *l, const char* repo);
int		laymanAPIIsInstalled(LaymanAPI *l, const char* repo);
StringList*	laymanAPIGetAvailable(LaymanAPI*, int reload);
StringList*	laymanAPIGetInstalled(LaymanAPI*, int reload);
int		laymanAPISync(LaymanAPI* l, const char* overlay, int verbose);
int 		laymanAPIFetchRemoteList(LaymanAPI*);
int		laymanAPIGetInfoStrList(LaymanAPI* l, StringList* overlays, OverlayInfo* results);
OverlayInfo*	laymanAPIGetInfoStr(LaymanAPI* l, const char* overlay);
int		laymanAPIGetAllInfoList(LaymanAPI* l, StringList*, OverlayInfo*);
OverlayInfo*	laymanAPIGetAllInfo(LaymanAPI* l, const char*);
int		laymanAPIAddRepo(LaymanAPI* l, const char *repo);
int		laymanAPIAddRepoList(LaymanAPI* l, StringList *repos);
int		laymanAPIDeleteRepo(LaymanAPI* l, const char *repo);
int		laymanAPIDeleteRepoList(LaymanAPI* l, StringList *repos);
OverlayInfo*	laymanAPIGetInfo(LaymanAPI* l, const char* overlay);
void		laymanAPIFree(LaymanAPI*);
void		overlayInfoFree(OverlayInfo oi);

#endif
