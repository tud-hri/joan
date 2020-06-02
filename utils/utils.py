class Biquad:
    def __init__(self):
        ## to get the appropriate variables you can use matlab to create a butterworth filter with:
        # [B,A] = butter(N,Wn) where N is the order and Wn the cutoff frequence divided by half the sample frequency (Fc/(Fs/2))

        #self.a = [1.000000000000000, -1.822694925196308, 0.837181651256023] #Fc 10hz at sample freq of 500Hz
        #self.b = [0.003621681514929, 0.007243363029857, 0.003621681514929]

        self.a = [1.000000000000000, -1.475480443592646, 0.586919508061190] #Fc 30Hz at sample freq of 500Hz
        self.b = [0.027859766117136, 0.055719532234272, 0.027859766117136] 

        self.y_1 = 0
        self.y_2 = 0
        self.x_1 = 0
        self.x_2 = 0

    def process(self, x: float):
        y = -self.a[1]*self.y_1 - self.a[2]*self.y_2 + x*self.b[0] + self.x_1*self.b[1] + self.x_2*self.b[2]
        self.y_2 = self.y_1
        self.y_1 = y
        self.x_2 = self.x_1
        self.x_1 = x

        return float(y)