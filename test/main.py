# EML test script.
# This script is programmed for Raspberry Pi Pico with Micropython.

from machine import Pin
from time import sleep

class ElectromagneticLauncher():
    def __init__(self):        
        self.charger_switch = Pin(7, Pin.OUT, Pin.PULL_DOWN) #电容充电（MOS管控制）
        self.led_indicator = Pin(25, Pin.OUT, Pin.PULL_DOWN) #RPi Pico 板载LED
        self.trigger = Pin(8, Pin.IN, Pin.PULL_DOWN) #激发按钮
        self.ScRs = [] #多个输出IO口，可控硅栅极控制线圈激发
        self.IRs = [] #多个输入IO口，红外光耦传感器检测发射物位置
        
        self.capacitor_state = 0 #电容电压状态机（0 - 未充电低电压，1 - 已充电高电压）
        self.charge_duration = 2 #电容充电时间（秒）
        self.accelerator_number = 4 #加速级数
        self.delay = [0, 0, 0] #光耦传感触发后延时特定秒数导通可控硅
        self.max_waiting_time = 20000 #等待光耦信号的时间上限 用于光耦未测到发射物位置没有给出信号时，跳出信号检测循环
        
        self.initialize_accelerators()
    
    def initialize_accelerators(self):
        #为每个可控硅门级和光耦传感器输出分配IO口
        for IO_num in range(self.accelerator_number):
            self.ScRs.append(Pin(IO_num, Pin.OUT, Pin.PULL_DOWN))
        for IO_num in range(self.accelerator_number, self.accelerator_number*2 - 1):
            self.IRs.append(Pin(IO_num, Pin.IN, Pin.PULL_DOWN))
    
    def update_capacitor_state(self):
        #更新电容和指示灯状态
        if self.capacitor_state:
            self.capacitor_state = 0
        else:
            self.capacitor_state = 1
        self.led_indicator.value(self.capacitor_state)
    
    def countdown(self):
        for i in range(10):
            self.led_indicator.value(1)
            sleep(0.25)
            self.led_indicator.value(0)
            sleep(0.25)

    def charge_capacitors(self):
        #按照设定的时间给电容充电并更新状态
        for ScR in self.ScRs:
            ScR.value(0) #充电前断开所有可控硅
        self.charger_switch.value(1)
        sleep(self.charge_duration)
        self.charger_switch.value(0)
        self.update_capacitor_state()
    
    def discharge_capacitors(self):
        for ScR in self.ScRs:
            ScR.value(1)
    
    def fire(self):
        self.led_indicator.value(1)
        self.ScRs[0].value(1) #进行初级加速
        sleep(3)
        self.ScRs[0].value(0)
        self.led_indicator.value(0)
        """
        for IR_index in range(len(self.IRs)):
            waiting_time = 0 #记录等待时间
            while waiting_time < self.max_waiting_time:
                if self.IRs[IR_index].value(): #读取光耦信号
                    sleep(self.delay[IR_index])
                    self.ScRs[IR_index + 1].value(1) #导通对应的可控硅
                    break
                waiting_time += 1
        """
        #self.update_capacitor_state()

if __name__ == "__main__":
    eml = ElectromagneticLauncher()
    while True:
        if eml.trigger.value():
            eml.countdown()
            eml.fire()
        sleep(0.1)
            
    

















