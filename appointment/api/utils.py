import datetime
   
def slot_generator(start_time, end_time, slot_duration):
    slot_list=[]
    start_time = datetime.datetime.combine(datetime.datetime.today(), start_time)
    end_time = datetime.datetime.combine(datetime.datetime.today(), end_time)

    current = start_time

    while current + slot_duration <= end_time:
        slot_list.append(current.time())
        current += slot_duration 
    return slot_list           

        

