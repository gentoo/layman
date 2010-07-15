//#include "overlay.h"
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
	
	Message *msg = messageCreate("layman", 0, 0, 0, 4, 2, 4, 4, 1, NULL, NULL, NULL);
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
	OverlayInfo *infos = malloc(sizeof(OverlayInfo) * len);
	int count = laymanAPIGetInfoList(l, strs, infos);
	
	for (unsigned int i = 0; i < count; i++)
	{
		printf("%s\n", infos[i].text);
		free(infos[i].text);
		free(infos[i].name);
	}

	printf("\n");

	free(infos);

	bareConfigFree(cfg);
	laymanAPIFree(l);
	stringListFree(strs);

	interpreterFinalize();

	return ret;
}
