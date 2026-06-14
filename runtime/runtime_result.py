class RuntimeResult:

    def __init__(self, success, output=None, error=None):
        self.success = success
        self.output = output
        self.error = error

    def to_dict(self):
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error
        }

    # Add this so printing the object directly looks readable!
    def __repr__(self):
        return f"RuntimeResult(success={self.success}, output={self.output}, error={self.error})"