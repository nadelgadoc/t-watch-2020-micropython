#!/opt/bin/lv_micropython -i
import cmath
import lvgl as lv
import display_driver
from lv_colors import lv_colors
import utime as time

# Line defined by polar coords; origin and line are complex
def polar(canvas, origin, line, width, color):
    line_dsc = lv.draw_line_dsc_t()
    line_dsc.init()
    line_dsc.color = color
    line_dsc.width = width
    p1=lv.point_t()
    p2=lv.point_t()    
    point_array=[p1,p2]
    
    xs, ys = origin.real, origin.imag
    p1.x=round(xs)
    p1.y=round(ys)
    p2.x=round(xs + line.real)
    p2.y=round(ys - line.imag)
    # print("x0: %d, y0: %d, x1: %d, y1: %d"%(round(xs), round(ys), round(xs + line.real), round(ys - line.imag)))
    canvas.draw_line(point_array, 2, line_dsc)

def conj(v):  # complex conjugate
    return v.real - v.imag * 1j

# Calculate the week day

def dayOfWeek(year,month,day):

    centuryCodeTable={
        1700: 4,
        1800: 2,
        1900: 0,
        2000: 6,
        2100: 4,
        2200: 2,
        2300: 0,
    }
    
    monthCodeTable = {
        1: 0,
        2: 3,
        3: 3,
        4: 6,
        5: 1,
        6: 4,
        7: 6,
        8: 2,
        9: 5,
        10: 0,
        11: 3,
        12: 5
    }
    
    y=year%100 # take only
    yearCode = y//4 + y
    yearCode %= 7

    # print("Year code: ",yearCode)

    century = year//100 * 100
    
    centuryCode =  centuryCodeTable[century]
    # print("Century Code: ",centuryCode)
    if year % 400 == 0:
        leapYearCode = 1
    elif year % 100 == 0:
        leapyearCode = 0
    elif year % 4 == 0:
        leapYearCode = 1
    else:
        leapYearCode = 0
        
    monthCode = monthCodeTable[month]
    dayCode = yearCode + monthCode + centuryCode +day
    # print("leapYearCode: ",leapYearCode)
    if month == 1 or month == 2:
        dayCode -= leapYearCode
        
    return dayCode % 7

def dayOfWeekString(dayCode):
    weekDayTable= {
        0: "Sun",
        1: "Mon",
        2: "Tue",
        3: "Wed",
        4: "Thu",
        5: "Fri",
        6: "Sat",
    }
    return weekDayTable[dayCode]

def monthString (monthCode):
    monthTable= {
        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dec",
    }
    return monthTable[monthCode]

class analogueClock():
    oldYear=-1
    oldMonth=-1
    oldDay=-1
    oldHour=-1
    oldMin=-1
    oldSec=-1
    oldDate=[oldYear,oldMonth,oldDay]

    def __init__(self,parent):
        
        self.CANVAS_HEIGHT = lv.scr_act().get_disp().driver.ver_res
        self.CANVAS_WIDTH = self.CANVAS_HEIGHT
        cbuf=bytearray(self.CANVAS_HEIGHT * self.CANVAS_HEIGHT * 4)

        self.canvas = lv.canvas(parent,None)
        self.canvas.set_buffer(cbuf,self.CANVAS_HEIGHT,self.CANVAS_HEIGHT,lv.img.CF.TRUE_COLOR)
        self.canvas.align(None,lv.ALIGN.CENTER,0,0)
        
        circle_dsc = lv.draw_line_dsc_t()
        circle_dsc.init()
        circle_dsc.color = lv_colors.GREEN
        self.radius = 90
        xo=self.CANVAS_WIDTH//2
        yo=self.CANVAS_HEIGHT//2-20
        self.canvas.draw_arc(xo,yo,self.radius,0,360,circle_dsc)
        vor = xo + 1j * yo
        vtstart = 0.9 * self.radius + 0j  # start of tick
        vtick = 0.1 * self.radius + 0j  # tick
        vrot = cmath.exp(2j * cmath.pi/12)  # unit rotation
        for _ in range(12):
            polar(self.canvas, vor + conj(vtstart), vtick, 1, lv_colors.GREEN)
            vtick *= vrot
            vtstart *= vrot
            
        vtick = 0.05 * self.radius + 0j  # tick
        vrot = cmath.exp(2j * cmath.pi/60)  # unit rotation
        for _ in range(60):
            polar(self.canvas, vor + conj(vtstart), vtick, 1, lv_colors.GREEN)
            vtick *= vrot
            vtstart *= vrot
            self.hrs_radius = self.radius-32
            self.min_radius = self.radius -12
            self.sec_radius = self.radius -12

        self.task = lv.task_create_basic()
        self.task.set_cb(lambda task: self.updateClock(self.task))
        self.task.set_period(100)
        self.task.set_prio(lv.TASK_PRIO.LOWEST)
        
    def updateClock(self,task):
        center=120+100j
        try:
            localTime = cetTime()
        except:
            now = time.time()
            localTime = time.localtime(now)
        seconds = localTime[5]
        minutes = localTime[4]
        hours = localTime[3]
        year = localTime[0]
        month = localTime[1]
        day= localTime[2]
        
        # print('{}:{}:{}'.format(hours,minutes,seconds))
    
        if hours > 12:
            hours -= 12
        hours *=5             # the angle corresponding to the hour 
        hours += 5/60*minutes # add the angle corresponding to the minutes

        theta = cmath.pi/2 - 2*hours*cmath.pi/60
        hrs_endpoint= cmath.rect(self.hrs_radius,theta)
        polar(self.canvas,center,hrs_endpoint,3,lv_colors.RED)
    
        theta = cmath.pi/2 - 2*minutes*cmath.pi/60
        min_endpoint= cmath.rect(self.min_radius,theta)
        polar(self.canvas,center,min_endpoint,3,lv_colors.RED)
    
        # clear the old hands 
        if self.oldSec != seconds:
            theta = cmath.pi/2 - 2*self.oldSec*cmath.pi/60
            sec_endpoint= cmath.rect(self.sec_radius+2,theta)
            polar(self.canvas,center,sec_endpoint,5,lv_colors.BLACK)
        
        if self.oldMin != minutes:
            theta = cmath.pi/2 - 2*self.oldMin*cmath.pi/60
            min_endpoint= cmath.rect(self.min_radius+2,theta)
            polar(self.canvas,center,min_endpoint,7,lv_colors.BLACK)
            
            theta = cmath.pi/2 - 2*self.oldHour*cmath.pi/60
            hrs_endpoint= cmath.rect(self.hrs_radius+2,theta)
            polar(self.canvas,center,hrs_endpoint,7,lv_colors.BLACK)

        # set the new hands according to the current time
    
        theta = cmath.pi/2 - 2*hours*cmath.pi/60
        hrs_endpoint= cmath.rect(self.hrs_radius,theta)
        polar(self.canvas,center,hrs_endpoint,3,lv_colors.RED)
    
        theta = cmath.pi/2 - 2*minutes*cmath.pi/60
        min_endpoint= cmath.rect(self.min_radius,theta)
        polar(self.canvas,center,min_endpoint,3,lv_colors.RED)
    
        theta = cmath.pi/2 - 2*seconds*cmath.pi/60
        sec_endpoint= cmath.rect(self.sec_radius,theta)
        polar(self.canvas,center,sec_endpoint,1,lv_colors.WHITE)
    
        self.oldSec=seconds
        self.oldMin=minutes
        self.oldHour=hours
    
        date = [year,month,day]
        if self.oldDate != date:
            # clear old date overwriting it with a black rectangle
            rect_dsc = lv.draw_rect_dsc_t()
            rect_dsc.init()
            rect_dsc.bg_color=lv_colors.BLACK
            rect_dsc.bg_opa=lv.OPA.COVER
            self.canvas.draw_rect(0,self.CANVAS_HEIGHT-30,self.CANVAS_WIDTH,20,rect_dsc)
        
            # write new date
            weekday = dayOfWeek(year,month,day)
            dateText=dayOfWeekString(weekday) + " " + str(day) + '.' + monthString(month) + ' ' + str(year)
            label_dsc = lv.draw_label_dsc_t()
            label_dsc.init()
            label_dsc.color=lv_colors.WHITE
            self.canvas.draw_text(0,self.CANVAS_HEIGHT-30,self.CANVAS_WIDTH,
                                  label_dsc,dateText,lv.label.ALIGN.CENTER)
            self.oldDate = date
                 
scr_style = lv.style_t()
scr_style.set_bg_color(lv.STATE.DEFAULT, lv_colors.BLACK)
lv.scr_act().add_style(lv.obj.PART.MAIN,scr_style)

text_style = lv.style_t()
text_style.init()
text_style.set_text_color(lv.STATE.DEFAULT,lv_colors.WHITE)

label = lv.label(lv.scr_act(),None)
label.set_text("Starting up...")
label.align(None,lv.ALIGN.CENTER, 0, 0)

try:
    from wifi_connect import connect,cetTime
    # get time from the network
    connect()
except:
    pass
    
label.delete()
aClock = analogueClock(lv.scr_act())