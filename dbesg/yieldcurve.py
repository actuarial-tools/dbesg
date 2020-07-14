import numpy as np
from scipy.optimize import minimize_scalar

class SmithWilson:
    
    """
        Example
        -------
            >>> maturity = np.array([1, 3, 5, 10, 20, 30])
            >>> rate = np.array([0.01301, 0.01325, 0.01415, 0.01600, 0.01625, 0.01604])
            >>> alpha, ufr = 0.1, 0.052
            >>> sw = SmithWilson(alpha, ufr)
            >>> sw.set_zeta(maturity, rate)
    """
    
    def __init__(self, alpha, ufr):
        self.alpha = alpha
        self.ufr = np.log(1+ufr)
        
    def discount_factor(self, t, order=0):
        """
            Description
            -----------
            할인요소(P(t))를 계산
            2nd derivatives까지 계산 가능함
        """

        df = (-self.ufr)**order*np.exp(-self.ufr*t)+self._wilson(t[:, None], self.u, self.alpha, order)@self.zeta
        return df

    def set_zeta(self, maturity, rate):
        """
            Description
            -----------
            관찰 금리 데이터를 이용해 ζ를 계산 후 객체 내에 저장

            Warning
            -------
            입력할 때 연단위(Annually compounded) 금리를 넣을 것
        """

        m = 1/(1+rate)**maturity
        mu = np.exp(-self.ufr*maturity)

        W = self._wilson(maturity[:, None], maturity, self.alpha)
        self.zeta = np.linalg.inv(W)@(m-mu)
        self.u = maturity.copy()
        
    def spot_rate(self, t, compounded='annually'):
        """
            Description
            -----------
            현물이자율(r(t))를 계산
        """

        t = np.fmax(t, 1e-6)
        P = np.exp(-self.ufr*t)+self._wilson(t[:, None], self.u, self.alpha)@self.zeta
        if compounded == 'annually':
            rate = (1/P)**(1/t) - 1
        elif compounded == 'continuously':
            rate = -np.log(P)/t
        else:
            raise Exception('compounded 입력 예외')
        return rate

    def forward_rate(self, t, s, compounded='annually'):
        """
            Description
            -----------
            선도이자율(f(t, t+s))를 계산
        """

        if s<0:
            raise Exception("s < 0 예외")
        if compounded == 'annually':
            rate = (self.discount_factor(t)/self.discount_factor(t+s))**(1/s)-1
        elif compounded == 'continuously':
            rate = 1/s*np.log(self.discount_factor(t)/self.discount_factor(t+s))
        else:
            raise Exception('compounded 입력 예외')
        return rate
    
    def instantaneous_forward_rate(self, t, order=0):
        """
            Description
            -----------
            순간선도이자율(f(t))를 계산
            instantaneous_forward_rate(t) ≒ forward_rate(t, 1e-6, compounded="continuously")
            1st derivatives까지 계산 가능함
        """

        if order==0:
            rate = -self.discount_factor(t, 1)/self.discount_factor(t, 0)
        elif order==1:
            rate = 1/self.discount_factor(t, 0)*(-self.discount_factor(t, 1)**2/self.discount_factor(t, 0)+self.discount_factor(t, 2))
        else:
            raise Exception('유효한 order가 아닙니다.')
        return rate
    
    def _wilson(self, t, u, alpha, order=0):
        if order == 0:
            W = np.exp(-self.ufr*(t+u))*(alpha*np.fmin(t,u) - np.exp(-alpha*np.fmax(t,u))*np.sinh(alpha*np.fmin(t,u)))
        elif order == 1:
            W = np.where(t < u, np.exp(-self.ufr*t-(alpha+self.ufr)*u)*(self.ufr*np.sinh(alpha*t)-alpha*np.cosh(alpha*t)-alpha*(self.ufr*t-1)*np.exp(alpha*u)), \
                    np.exp(-self.ufr*u-(alpha+self.ufr)*t)*((alpha+self.ufr)*np.sinh(alpha*u)-alpha*self.ufr*u*np.exp(alpha*t)))
        elif order == 2:
            W = np.where(t < u, np.exp(-self.ufr*t-(alpha+self.ufr)*u)*(-(alpha**2+self.ufr**2)*np.sinh(alpha*t)+2*alpha*self.ufr*np.cosh(alpha*t)+alpha*self.ufr*(self.ufr*t-2)*np.exp(alpha*u)), \
                    np.exp(-self.ufr*u-(alpha+self.ufr)*t)*(alpha*self.ufr**2*u*np.exp(alpha*t)-(alpha+self.ufr)**2*np.sinh(alpha*u)))
        else:
            raise Exception('유효한 order가 아닙니다.')
        return W