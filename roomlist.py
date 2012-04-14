#!/usr/bin/env python
import sys
import string

from gi.repository import GObject
GObject.threads_init()

from gi.repository import TelepathyGLib

import dbus
from dbus.mainloop.glib import DBusGMainLoop

import pprint
import inspect

def dump(what):
    pprint.pprint(inspect.getmembers(what), indent=2)

def dumpclass(which):
    print which
    pprint.pprint(dir(which), indent=2)

def listing_rooms_cb(is_listing):
    if False == is_listing:
        channel.close_async(None, None)
        main_loop.quit()

def got_rooms_cb(therooms):
#    dbus.Struct(
#            (dbus.UInt32(29L),
#            dbus.String(u'org.freedesktop.Telepathy.Channel.Type.Text'),
#            dbus.Dictionary({
#                dbus.String(u'name'): dbus.String(u'', variant_level=1),
#                dbus.String(u'members-only'): dbus.Boolean(False, variant_level=1),
#                dbus.String(u'persistent'): dbus.Boolean(True, variant_level=1),
#                dbus.String(u'moderated'): dbus.Boolean(False, variant_level=1),
#                dbus.String(u'handle-name'): dbus.String(u'', variant_level=1),
#                dbus.String(u'members'): dbus.UInt32(2L, variant_level=1),
#                dbus.String(u'invite-only'): dbus.Boolean(False, variant_level=1),
#                dbus.String(u'hidden'): dbus.Boolean(False, variant_level=1),
#                dbus.String(u'password'): dbus.Boolean(True, variant_level=1),
#                dbus.String(u'anonymous'): dbus.Boolean(False, variant_level=1)
#                },
#                signature=dbus.Signature('sv'))
#            ),
#    signature=None)
        
    for (_, channel_type, room_info) in therooms:
        print "%s %s %s" % (_, room_info['name'], room_info['handle-name'])

def channel_prepared_cb(channel, result, data):
    success = channel.prepare_finish(result)

    roomlist = session_bus.get_object(channel.get_bus_name(), channel.get_object_path())
    iface = dbus.Interface(roomlist, dbus_interface=TelepathyGLib.IFACE_CHANNEL_TYPE_ROOM_LIST)
    
    iface.connect_to_signal('GotRooms', got_rooms_cb)
    iface.connect_to_signal('ListingRooms', listing_rooms_cb)
    iface.ListRooms()

def create_channel_cb(request, result, data):
    global channel
    channel, context = request.create_and_handle_channel_finish(result)
    channel.prepare_async(None, channel_prepared_cb, None)

def account_prepared_cb(account, result, data):
    success = account.prepare_finish(result)

    request_dict = {TelepathyGLib.PROP_CHANNEL_CHANNEL_TYPE: TelepathyGLib.IFACE_CHANNEL_TYPE_ROOM_LIST,
                    TelepathyGLib.PROP_CHANNEL_TARGET_HANDLE_TYPE: int(TelepathyGLib.HandleType.NONE),
                    TelepathyGLib.PROP_CHANNEL_TYPE_ROOM_LIST_SERVER: ''}
    
    request = TelepathyGLib.AccountChannelRequest.new(account, request_dict, 0)
    request.create_and_handle_channel_async(None, create_channel_cb, None)

def manager_prepared_cb(account_manager, result, data):
    account_manager.prepare_finish(result)
    account = account_manager.ensure_account(account_path)
    account.prepare_async(None, account_prepared_cb, None);
    
def manager_prepare():
    account_manager = TelepathyGLib.AccountManager.dup()
    account_manager.prepare_async(None, manager_prepared_cb, None)

def path_encode_jid(jid):
    path = jid
    path = string.replace(path, '@', '_40')
    path = string.replace(path, '.', '_2e')
    path = "%sgabble/jabber/%s0" % (TelepathyGLib.ACCOUNT_OBJECT_PATH_BASE, path)
    return path

if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)
    main_loop = GObject.MainLoop()

    if len(sys.argv) < 2:
        print "Usage: %s <jid>" % sys.argv[0]
        sys.exit(1)

    account_path = path_encode_jid(sys.argv[1])
    
    session_bus = dbus.SessionBus()

    manager_prepare()  
    main_loop.run()
