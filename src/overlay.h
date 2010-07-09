#ifndef OVERLAY_H
#define OVERLAY_H

typedef struct Overlay Overlay;

Overlay*	createOverlay(const char*, const char*, int, int);
const char*	overlayName(Overlay*);
const char*	overlayOwnerEmail(Overlay*);
const char*	overlayDescription(Overlay*);
const char*	overlayShortList(Overlay *o);
const char*	overlayStr(Overlay *o);
const char*	overlayToXml(Overlay *o);
int 		overlayPriority(Overlay*);
int 		overlayIsOfficial(Overlay*);
int		overlayIsSupported(Overlay *o);
void		overlayFree(Overlay*);

#endif
