#ifndef OVERLAY_H
#define OVERLAY_H

//TODO:document me !

typedef struct Overlay Overlay;

Overlay*	createOverlay(const char*, const char*, int, int);
const char*	overlayName(Overlay*);
const char*	overlayOwnerEmail(Overlay*);
const char*	overlayDescription(Overlay*);
const char*	overlayShortList(Overlay*);
const char*	overlayStr(Overlay*);
const char*	overlayToXml(Overlay*);
int 		overlayPriority(Overlay*);
int 		overlayIsOfficial(Overlay*);
int		overlayIsSupported(Overlay*);
void		overlayFree(Overlay*);

#endif
