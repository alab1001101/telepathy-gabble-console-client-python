#!/usr/bin/env python
import sys
import string

from gi.repository import GObject
GObject.threads_init()

from gi.repository import TelepathyGLib

import pprint
import inspect

def dump(what):
    pprint.pprint(inspect.getmembers(what), indent=2)

def dumpclass(which):
    pprint.pprint(dir(which), indent=2)

def channel_prepared_cb(channel, result, main_loop):
    success = channel.prepare_finish(result)
    print "Prepare finish returned: %s" % success
    print "Channel Type is: %s" % channel.get_channel_type()
    print "Interfaces: %s" % channel.get_properties('interfaces')
    print "Channel Object Path: %s" % channel.get_object_path()
    has_iface = channel.has_interface(TelepathyGLib.IFACE_CHANNEL_TYPE_ROOM_LIST)
    print "Channel has Interface %s: %s" % (TelepathyGLib.IFACE_CHANNEL_TYPE_ROOM_LIST, has_iface)

    print "Here i would like to call ListRooms() from Interface %s" % TelepathyGLib.IFACE_CHANNEL_TYPE_ROOM_LIST
    print "Unfortunatly it's not available on object channel"
    #dumpclass(channel)
    
    channel.close_async(None, None)
    main_loop.quit()

def create_channel_cb(request, result, main_loop):
    channel, context = request.create_and_handle_channel_finish(result)
    #channel.prepare_async([TelepathyGLib.iface_quark_channel_type_room_list()], channel_prepared_cb, main_loop)
    channel.prepare_async(None, channel_prepared_cb, main_loop)

def manager_prepared_cb(account_manager, result, main_loop):
    account_manager.prepare_finish(result)

    account = account_manager.ensure_account(account_path)
    print "Account object_path: %s" % account.get_object_path()
    
    request_dict = {TelepathyGLib.PROP_CHANNEL_CHANNEL_TYPE: TelepathyGLib.IFACE_CHANNEL_TYPE_ROOM_LIST,
                    TelepathyGLib.PROP_CHANNEL_TARGET_HANDLE_TYPE: int(TelepathyGLib.HandleType.NONE),
                    TelepathyGLib.PROP_CHANNEL_TYPE_ROOM_LIST_SERVER: ''}
    
    request = TelepathyGLib.AccountChannelRequest.new(account, request_dict, 0)
    request.create_and_handle_channel_async(None, create_channel_cb, main_loop)
    
def manager_prepare(main_loop):
    account_manager = TelepathyGLib.AccountManager.dup()
    account_manager.prepare_async(None, manager_prepared_cb, main_loop)

def path_encode_jid(jid):
    path = jid
    path = string.replace(path, '@', '_40')
    path = string.replace(path, '.', '_2e')
    path = "%sgabble/jabber/%s0" % (TelepathyGLib.ACCOUNT_OBJECT_PATH_BASE, path)
    return path

if __name__ == '__main__':
    main_loop = GObject.MainLoop()
    
    if len(sys.argv) < 2:
        print "Usage: %s <jid>" % sys.argv[0]
        sys.exit(1)

    account_path = path_encode_jid(sys.argv[1])
    
    manager_prepare(main_loop)  
    main_loop.run()
