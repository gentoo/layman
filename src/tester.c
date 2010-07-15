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
	for (unsigned int i = 0; i < len; i++)
	{
		OverlayInfo *info = laymanAPIGetInfo(l, stringListGetAt(strs, i));
		if (!info)
			continue;
		printf("%s\n", info->text);
		free(info->text);
		free(info);
	}

	printf("\n");

finish:
	bareConfigFree(cfg);
	laymanAPIFree(l);
	stringListFree(strs);

	interpreterFinalize();

	return ret;
}
