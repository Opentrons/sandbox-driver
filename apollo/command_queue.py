import copy
import datetime
import uuid


class CommandQueue(object):
    """
    This object stores commands FIFO and tracks information about them as they are processed.


    Commands are stored in two lists:

    "command_queue" : Commands yet to be completed
    "completed" : Commands completed

    Commands are added to the end of the "command_queue" with add_command(command)

    Commands are retrieved FIFO with next(), moving the "current_command" being processed
    to "completed" and returning the .
    """

    def __init__(self):
        self._size = 0

        self._command_queue = []

        self._completed = []

        self._current_command = None

        self._counter = 0


    @property
    def size(self):
        """ Number of commands in queue """
        return self._size

    def add_command(self, command):
        """ Add a command to the queue
        """
        if command is not None:
            self._counter += 1
            self._command_element = {'uid': uuid.uuid4(),
                                     'number': self._counter,
                                     't_add': datetime.datetime.utcnow(),
                                     't_out': 'na',
                                     't_com': 'na',
                                     'command': command,
                                     'result': 'tbd'}
            self._command_queue.append(self._command_element)
            self._size = len(self._command_queue)
        else:
            return False

    def next(self, result='success', show_all=False):
        """ Return the next command if there is one and move the current command to the
            completed list with a note about its result.
        """
        if self._size > 0:
            if self._current_command is not None:
                self._current_command['t_com'] = datetime.datetime.utcnow()
                self._current_command['result'] = result

                self._completed.append(self._current_command)

            self._size = len(self._command_queue)

            self._current_command = self._command_queue.pop(0)
            self._current_command['t_out'] = datetime.datetime.utcnow()
            return_command = copy.deepcopy(self._current_command)

            if show_all == True:
                return return_command
            else:
                return return_command['command']

        return None

    # @property? read-only getter
    def completed(self):
        """ Return a read-only copy of the completed list """
        return copy.deepcopy(self._completed)


    #@property? read-only getter
    def command_queue(self, show_all=False):
        """
        Get a copy of the "command queue". Only sends the actual commands by default.
        If you want the "command queue" in all its gory details, pass 'show_all' as True
        """
        if show_all == True:
            return copy.deepcopy(self._command_queue)
        else:
            command_list = [c['command'] for c in self._command_queue]
            return command_list


    def flush_completed(self):
        """ Flush "the completed queue" """
        self._completed = []


    def clear_queue(self, save_cleared=False):
        """
        Clear the "command queue", and if you want to save the entries to
        the "completed lists" pass save_cleared as True
        """
        if save_cleared == False:
            self._command_queue = []
        else:
            for c in self._command_queue: c[
                't_com'] = datetime.datetime.utcnow()
            for c in self._command_queue: c['result'] = 'cleared'
            self._completed.append(self._command_queue)
            self._command_queue = []
        self._counter = 0
        self._size = 0

