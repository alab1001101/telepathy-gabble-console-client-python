#!/usr/bin/python

import os
import pprint

from gi.repository import GObject
GObject.threads_init()

from gi.repository import TelepathyGLib as Tp

import cmd

class Lala(cmd.Cmd):
    """Simple command processor example."""
    
    prompt = 'account> '

    restart = False

    # 'AVAILABLE', 'AWAY', 'BUSY', 'ERROR', 'EXTENDED_AWAY', 'HIDDEN', 'OFFLINE', 'UNKNOWN', 'UNSET'

    presenceTypes = { 'available': Tp.ConnectionPresenceType.AVAILABLE
		    , 'away':      Tp.ConnectionPresenceType.AWAY
		    , 'busy':      Tp.ConnectionPresenceType.BUSY
		    , 'hidden':    Tp.ConnectionPresenceType.HIDDEN
		    , 'offline':   Tp.ConnectionPresenceType.OFFLINE
		    }

    def do_list(self, line):
        """list accounts"""
        for account in getAccounts():
            printAccount(account)

    def do_presence(self, line):
	args = (line.split(" ") + ["","",""])
	account = getAccountByName(args[0])
	if account is not None and len(args) > 1:
            account.request_presence_async(self.presenceTypes[args[1]], args[1], args[2], account_presence_cb, None)
	    self.restart = True
	    return True

    def complete_presence(self, text, line, begidx, endidx):
	count = len(line.split(" "))

	if count == 2:
	    completions = getAccountNames()
	elif count == 3:
	    completions = self.presenceTypes.keys()

        if text:
	    completions = [ f for f in completions if f.startswith(text) ]

        return completions

    def do_quit(self, line):
	self.restart = False
        return True
    
    def do_EOF(self, line):
	print
	self.restart = False
        return True
    
    #def postloop(self):
    #    print

def printAccount(account):
    print "%s %s %s %s" % ((account.get_service(), account.get_normalized_name()) + account.get_current_presence()[1:])

def getAccountByName(name):
    for account in getAccounts():
        if name == account.get_normalized_name():
	    return account
    return None

def getAccountNames():
    names = []
    for account in getAccounts():
        names.append(account.get_normalized_name())
    return names

def getAccounts():
    return manager.get_valid_accounts()

def account_presence_cb(account, result, args):
    account.request_presence_finish(result)
    reloop()

def reloop():
    lala.cmdloop()
    if False == lala.restart:
        loop.quit()

def manager_prepared_cb(manager, result, loop):
    manager.prepare_finish(result)

    reloop()

def manager_prepare(loop):
    global manager

    if manager:
        del manager
	
    manager = Tp.AccountManager.dup()

    factory = manager.get_factory()
    factory.add_account_features([Tp.Account.get_feature_quark_connection()])

    manager.prepare_async(None, manager_prepared_cb, loop)

if __name__ == '__main__':
    Tp.debug_set_flags(os.getenv('EXAMPLE_DEBUG', ''))

    loop = GObject.MainLoop()
    lala = Lala()
    manager = None
    manager_prepare(loop)
    loop.run()
