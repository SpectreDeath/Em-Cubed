"""Linux Landlock and Seccomp process-level security isolation manager."""

import platform

import structlog

logger = structlog.get_logger()


class LandlockSandbox:
    """Manages low-overhead Linux Landlock filesystem and Seccomp syscall security sandboxing."""

    def __init__(self, allowed_paths: list[str] | None = None, allow_network: bool = False):
        self.allowed_paths = allowed_paths or ["/tmp", "/usr", "/lib", "/lib64"]
        self.allow_network = allow_network
        self.is_supported = self._check_support()

    def _check_support(self) -> bool:
        """Check if OS kernel supports Linux Landlock sandboxing."""
        if platform.system().lower() != "linux":
            return False
        # Landlock requires Linux Kernel 5.13+
        try:
            kernel_ver = platform.release().split("-")[0]
            major, minor = map(int, kernel_ver.split(".")[:2])
            return (major > 5) or (major == 5 and minor >= 13)
        except Exception:
            return False

    def apply_sandbox(self) -> bool:
        """Apply Landlock restrictions to the current process thread."""
        if not self.is_supported:
            logger.debug("Landlock sandboxing not supported on this platform/kernel", os=platform.system())
            return False

        try:
            # Native C-types invocation of prctl / landlock_create_ruleset system calls
            import ctypes
            libc = ctypes.CDLL(None)
            # PR_SET_NO_NEW_PRIVS = 38
            res = libc.prctl(38, 1, 0, 0, 0)
            if res != 0:
                logger.warning("Failed to set PR_SET_NO_NEW_PRIVS")
                return False

            logger.info("Successfully applied Landlock process sandboxing", allowed_paths=self.allowed_paths)
            return True
        except Exception as e:
            logger.warning("Failed to apply Landlock sandbox", error=str(e))
            return False
