import asyncio
import enum


class STATUS(enum.Enum):
    """
    Encapsulates status information about a job.
    """

    FAILURE = 0
    READY = 1
    STARTING = 2
    RUNNING = 3
    STOPING = 4
    FINISH = 5


class AsyncJob:
    """Encapsulates information about a job.

    Args:

        cmd: A string, or a sequence of program arguments.

        dependence : A AsyncJob object sequence of dependent task.

        shell : If true, the command will be executed through the shell.

        options : Valid arguments of subprocess protocol function.
    """

    def __init__(self, cmd, dependence=(), shell=False, **options) -> None:

        if not cmd:
            raise ValueError("Invalid command.")

        self.cmd = cmd
        self.dependence = dependence

        self.shell = shell
        self.options = options

        self._status = STATUS.READY
        self._events = {status: asyncio.Event() for status in STATUS}

    @property
    def status(self) -> STATUS:
        """The job's current status."""
        return self._status_

    @status.setter
    def status(self, value: STATUS):
        event = self._events[value]
        if not event.is_set():
            event.set()

        self._status = value

    @property
    def running(self) -> bool:
        """Check that the job is running."""
        return self._status_ is STATUS.RUNNING

    async def done(self, status: STATUS):
        """Wait for the job to complete the specified status."""
        if status in self._events:
            return self._events[status]

        event = asyncio.Event()

    async def run(self):
        """Create a subprocess to run command and wait for completion."""
        self.status = STATUS.STARTING

        for job in self.dependence:
            await job.done(STATUS.RUNNING)

        if self.shell:
            process = await asyncio.subprocess.create_subprocess_shell(
                cmd=self.cmd, **self.options
            )
        else:
            process = await asyncio.subprocess.create_subprocess_exec(
                cmd=self.cmd, **self.options
            )

        if process.returncode is None:
            self.status = STATUS.RUNNING
        elif process.returncode == 0:
            self.status = STATUS.FINISH
        else:
            self.status = STATUS.FAILURE
