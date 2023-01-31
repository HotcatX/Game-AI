class pid(object):
    def __init__(self, exp_val, P: float, I: float, D: float):
        self.Kp = P
        self.Ki = I
        self.Kd = D

        self.PIDOutput = 0.0
        self.SystemOutput = 0.0
        self.LastSystemOutput = 0.0

        self.Error = 0.0
        self.LastError = 0.0
        self.LastLastError = 0.0

    def cmd_pid(self, sub_s):
        self.Error = sub_s - self.SystemOutput

        IncrementalValue = self.Kp * (self.Error - self.LastError) \
                           + self.Ki * self.Error + self.Kd * (self.Error - 2 * self.LastError + self.LastLastError)

        self.PIDOutput += IncrementalValue
        self.LastLastError = self.LastError
        self.LastError = self.Error
        return self.PIDOutput 
