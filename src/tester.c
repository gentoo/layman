#include <stdlib.h>
#include "interpreter.h"
#include "config.h"
#include "laymanapi.h"
#include "message.h"

int main(int argc, char *argv[])
{
	argc = argc;
	argv = argv;
	int ret = 0;
	interpreterInit();
	
	Message *msg = messageCreate("layman", 0, 0, 0);
	BareConfig *cfg = bareConfigCreate(msg, 0, 0, 0);
	/*if (!bareConfigSetOptionValue(cfg, "local_list", "/home/detlev/src/gsoc2010/layman/layman/tests/testfiles/global-overlays.xml"))
		printf("Error setting config option.\n");
	if (!bareConfigSetOptionValue(cfg, "storage", "/home/detlev/gsoc2010/layman-test"))
		printf("Error setting config option.\n");
	printf("config: %s\n", bareConfigGetOptionValue(cfg, "config"));
	printf("storage: %s\n", bareConfigGetOptionValue(cfg, "storage"));
	printf("local_list: %s\n", bareConfigGetOptionValue(cfg, "local_list"));*/

	LaymanAPI *l = laymanAPICreate(cfg, 0, 0);
	/*if (0 == laymanAPIFetchRemoteList(l))
	{
		printf("Unable to fetch the remote list.\n");
		ret = -1;
		goto finish;
	}*/

	StringList *strs = laymanAPIGetAvailable(l, 0);
	printf("list:\n");
	stringListPrint(strs);
	
	printf("\n");

	unsigned int len = stringListCount(strs);
	//OverlayInfo *infos = calloc(len, sizeof(OverlayInfo));
	//int count = laymanAPIGetAllInfos(l, strs, infos);
	
	OverlayInfo *oi = laymanAPIGetAllInfo(l, "enlfdsightenment");
	if (oi)
	{
		printf("%s\n~~~~~~~~~~~~~~~~~~~~\n", oi->name);
		printf("%s\n\n", oi->description);
		overlayInfoFree(*oi);
		free(oi);
	}

	for (unsigned int i = 0; i < len; i++)
	{
		OverlayInfo *oi = laymanAPIGetAllInfo(l, stringListGetAt(strs, i));
		if (!oi)
			continue;
		printf("%s\n~~~~~~~~~~~~~~~~~~~~\n", oi->name);
		printf("%s\n\n", oi->description);
		overlayInfoFree(*oi);
		free(oi);
	}

	printf("\n");

	//free(infos);

	bareConfigFree(cfg);
	laymanAPIFree(l);
	stringListFree(strs);

	interpreterFinalize();

	return ret;
}
