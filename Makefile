OBS_PROJECT := EA4
OBS_PACKAGE := libcurl
DISABLE_BUILD := repository=CentOS_8 repository=CentOS_9
include $(EATOOLS_BUILD_DIR)obs.mk
