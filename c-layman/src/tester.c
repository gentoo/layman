#include <stdlib.h>

#include "interpreter.h"
#include "config.h"
#include "laymanapi.h"
#include "message.h"
#include "basic.h"
#include "stringlist.h"


void
output_errors(LaymanAPI *l)
{
	StringList *errors = laymanAPIGetErrors(l);
	if(errors == NULL)
		printf("Failed to get any errors\n");
	else
	{
		printf("Recorded errors were:\n");
		printf("Error count = %d\n", stringListCount(errors));
		stringListPrint(errors);
	}
}


int
test_fetch_remote(LaymanAPI *l)
/**/
{
	int ret;
	if (False == laymanAPIFetchRemoteList(l))
	{
		printf("Unable to fetch the remote list.\n");
		output_errors(l);
		ret = False;
	}
	else
		ret = True;
	return ret;
}

 
int 
main(int argc, char *argv[])
{
	argc = argc;
	argv = argv;
	int ret = 0;
	laymanInit();
	
	MessageStruct *msg = messageCreate( 0, 0, 4, 4, True);
	if(msg == NULL)
		printf("Failed to create a MessageStruct object\n");
	
	BareConfigStruct *cfg = bareConfigCreate(msg, 0, 0, 0);
	if(cfg == NULL)
		printf("Failed to create BareConfigStruct object\n");
	
	/*if (!bareConfigSetOptionValue(cfg, "local_list", 
		"/home/detlev/src/gsoc2010/layman/layman/tests/testfiles/global-overlays.xml"))
		printf("Error setting config option.\n");
	if (!bareConfigSetOptionValue(cfg, "storage", "/home/detlev/gsoc2010/layman-test"))
		printf("Error setting config option.\n");
	printf("config: %s\n", bareConfigGetOptionValue(cfg, "config"));
	printf("storage: %s\n", bareConfigGetOptionValue(cfg, "storage"));
	printf("local_list: %s\n", bareConfigGetOptionValue(cfg, "local_list"));*/

	LaymanAPI *l = laymanAPICreate(cfg, 0, 0);
	
	if(!test_fetch_remote(l))
		printf("\nFetch test failed.\n");

	StringList *strs = laymanAPIGetAvailable(l, 0);
	printf("list:\n");
	stringListPrint(strs);

	printf("\n");

	//unsigned int len = stringListCount(strs);
	//OverlayInfo *infos = calloc(len, sizeof(OverlayInfo));
	//int count = laymanAPIGetAllInfos(l, strs, infos);
	
	OverlayInfo *oi = laymanAPIGetAllInfo(l, "kuroo");
	if (oi)
	{
		printf("%s\n~~~~~~~~~~~~~~~~~~~~\n", oi->name);
		printf("%s\n\n", oi->description);
		overlayInfoFree(*oi);
		free(oi);
	}
	
	/*for (unsigned int i = 0; i < len; i++)
	{
		OverlayInfo *oi = laymanAPIGetAllInfo(l, stringListGetAt(strs, i));
		if (!oi)
			continue;
		printf("%s\n~~~~~~~~~~~~~~~~~~~~\n", oi->name);
		printf("%s\n\n", oi->description);
		overlayInfoFree(*oi);
		free(oi);
	}*/

	printf("\n");

	//free(infos);
	stringListFree(strs);

	ConfigFree(cfg);
	laymanAPIFree(l);

	laymanFinalize();

	return ret;
}
