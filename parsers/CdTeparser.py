import sys
import numpy as np
import polars as pl
import struct
import statistics

def CdTerawalldata2parser(datalist):
    framesize = 32776#;  #static const int // 32780-4 //16396-4
    framewordsize = 8194#;static const int

    eventsize = 2048#;static const int
    noofch = 64#;static const int
    numofchip = 16#;static const int
    numofallch_max = 2560#;static const int

    sizeofeventdatabit = 40960#;static const int

    hksize = 8192#;static const int  // 10288 byte;
    numofalladc_max = 40#;static const int

    framedata=[0]*framewordsize#];unsigned int
    eventdata=[0]*eventsize#;unsigned int
    data=[0]*8192#;unsigned int
    tmpdata=0#;unsigned char
    tmpintdata=0#;unsigned int

    asicdatabits=[0]*sizeofeventdatabit#;unsigned int

    numofdaisychains = 4#int ;
    numofasicperdaisychains = 1#int ;
    numofalladc= noofch * numofasicperdaisychains * numofdaisychains#int;; // = numofdaisychains * numofasicperdaisychains
    numofallch= numofdaisychains * numofasicperdaisychains#int ; // = noofch * numofasicperdaisychains * numofdaisychains

    #array_chflag[numofalladc_max][3]#unsigned int ;
    ##array_adc[numofalladc_max][noofch]#unsigned short ;
    array_ref=[0]*numofalladc_max#unsigned short ;
    array_cmn=[0]*numofalladc_max#unsigned short ;
    #array_index[numofalladc_max][noofch];unsigned short
    array_hitnum=[0]*numofalladc_max#;unsigned short
    array_cmn_ex=[0]*numofalladc_max#;double

    ti=0#;unsigned int
    livetime=0#;unsigned int
    integral_livetime=0#;unsigned int
    trighitpat=0#;unsigned int
    eventid=0#;unsigned int
    hkraw=[0]*hksize#unsigned int ;
    hk_readsize=0#;unsigned int
    unixtime=0#;unsigned int
    adcclkcnt=0#;unsigned short

    ti_upper=0#unsigned int ;
    ti_lower=0#;unsigned int
    ext1ti_upper=0#;unsigned int
    ext1ti_lower=0#unsigned int ;
    ext2ti_upper=0#unsigned int ;
    ext2ti_lower=0#;unsigned int
    pseudo_counter=0#;unsigned int
    flag_pseudo=0#;unsigned short
    flag_forcetrig=0#;unsigned short
    flag_bgo=0#;unsigned short

    framedataok=False#bool ;
    hkflag=False
    eventflag=False
    frameflag=False


    nword=0#  int ;
    amari=0#;  int
    tempint=0#;//  unsigned int
    i,j, k=0,0,0#  int ;
    ibit=0#  int ;
    l=0#  int ;
    offset = 0#  int ;
    isize = 0#  int ;
    iasic=0#  int ;
    idchain=0#  int ;
    framecount = 0#  int ;



    adc=[0]*noofch#unsigned short
    ref=0#              unsigned short
    cmn=0#              unsigned short ;
    chflag=[0]*3#              unsigned int ;
    index = [0]*noofch#              unsigned short ;
    hitnum = 0#              int ;

    framedataok = False
    unixtime = 0
    nlist=0
    nlist_max = len(datalist)
    eventid=0
    #print(nlist,nlist_max)

    Lti = []
    Lunixtime = []
    Llivetime = []
    Ladccmn_al = []
    Ladccmn_pt = []
    Lcmn_al=[]
    Lcmn_pt=[]
    Lindex_al =[]
    Lindex_pt =[]
    Lhitnum_al =[]
    Lhitnum_pt =[]
    Lflag_pseudo=[]
    #all_array_chflag=[]
    all_array_adc=[]
    all_array_index=[]
    hkflag=False
    eventflag=False
    errorflag=False

    all_hkdicts=[]




    while(True):
        if(nlist>=nlist_max):
           # print("************END: ALL DATA IS PROCESSED *********************")
            break

        tmpintdata=datalist[nlist]
        nlist+=1
        if( (tmpintdata & 0x00FFFFFF) != 0x00efcdab ):
            continue

        tmpdata = (tmpintdata & 0xFF000000) >> 24#;                //11111111000000000000000000000000(1*8,0*24)
        #print(tmpdata)

        #-----------------------------------------------HK  DATA----------------------------------------------------------------
        if(tmpdata == 0x03):# //11
            print("hkstart")
            i=0
            while(True):
                if(nlist>=nlist_max):
                    print("************ERROR: STOP in PROCESSING HK DATA, ***********************",nlist,nlist_max)
                    errorflag=False
                    break

                data[0]=datalist[nlist]
                nlist+=1

                if(data[0] == 0x2301FFFF):
                    print("hk finish")
                    hkflag=True
                    hk_readsize = i
                    #print(hkraw,hk_readsize)
                    list1=[format(i,"04x") for i in range(hk_readsize)]
                    #hktree->Fill();
                    framecount+=1
                    all_hkdicts.append(dict(zip(list1,hkraw)))
                    #if(eventflag and hkflag):
                        #errorflag = True
                        #print("CAUTION!! : INPUT DATA IS FRAME DATA? BOTH HK AND EVENT DATA ARE FOUND")
                    #return Flags,dict(zip(list1,hkraw))
                    break


                else:
                    hkraw[i] = ((data[0]&0xff000000)>>24) + ((data[0]&0x00ff0000)>>8)+ ((data[0]&0x0000ff00)<<8)+ ((data[0]&0x000000ff)<<24)#
                    i+=1




       #-----------------------------------------------Detector  DATA----------------------------------------------------------------

        elif(tmpdata == 0x02):#//10
            print("eventframestart")
            
            if(nlist+framewordsize>nlist_max):
                print("************Caution: STOP in PROCESSING EVENT DATA, LAST FRAME is BROKEN***********************",nlist,nlist_max)
                errorflag=True
                break
            
            framedata=datalist[nlist:nlist+framewordsize+1]
            nlist+=framewordsize
        
            try:
                if( not((framedata[framewordsize-1] == 0x2301FFFF))):
                    errorflag=True
                    print("************ERROR: FRAME DATA STRUCTURE( OF THE END) IS NOT CORRECT************")

                else:
                    unixtime =  framedata[framewordsize-2]
                    framedataok = True
                    
            except IndexError:
                # to test full files being artificially split-up  - kris
                print("A non-full frame was encountered.")
                break

            if(framedataok):
                j=0
                framecount+=1
                while(True):
                    while( (framedata[j] & 0x0000FFFF) != 0x00003c3c and j<framewordsize):
                        j+=1
                        if(j>=framewordsize):
                            break
                    i=0
                    offset = j
                    
                    if(j>=framewordsize):
                        print("eventframe end! Sum of Nevent:",eventid)
                        eventflag=True
                        break

                    while(framedata[j] != 0x77770000 and i<eventsize and  j<framewordsize):
                        eventdata[i] = ((framedata[j]&0xff000000)>>24)+ ((framedata[j]&0x00ff0000)>>8)+ ((framedata[j]&0x0000ff00)<<8)+ ((framedata[j]&0x000000ff)<<24)
                        j+=1
                        i+=1
                    isize = i

                    if(j>=framewordsize):
                        print("eventframe end! Sum of Nevent:",eventid)
                        eventflag=True
                        break

                    if(i >= eventsize):
                        j = offset +1

                    elif(j<framewordsize):
                        ti = eventdata[1]
                        livetime = eventdata[2]
                        integral_livetime = (eventdata[3] & 0xffff0000) >>16
                        flag_pseudo = (eventdata[3] & 0x00000001)
                        flag_forcetrig = (eventdata[3] & 0x00000002) >> 1
                        flag_bgo = (eventdata[3] & 0x0000003c) >> 2
                        trighitpat = (eventdata[3] & 0x0000ffc0) >> 6
                        adcclkcnt = 0

                        pseudo_counter = eventdata[6]
                        ti_upper = 0
                        ti_lower = 0
                        ext1ti_upper = eventdata[4]
                        ext1ti_lower = eventdata[5]
                        ext2ti_upper = 0
                        ext2ti_lower = 0

                        #if(eventid ==1):
                            #print(ti,livetime,integral_livetime,trighitpat)

                        #for(i=0;i<sizeofeventdatabit;i++):
                            #asicdatabits[i] = 0

                        for ibit in range(32*(isize-7)):
                            amari = ibit%32
                            nword =7+(ibit-amari)//32
                            asicdatabits[ibit] = (eventdata[nword] >> (31-amari)) & 0x00000001

                        bitoffset = 0;
                        for idchain in range(numofdaisychains):
                            for iasic in range(numofasicperdaisychains):
                                adc=[0]*noofch#unsigned short
                                ref=0#              unsigned short
                                cmn=0#              unsigned short ;
                                chflag=[0]*3#              unsigned int ;
                                index = [0]*noofch#              unsigned short ;
                                hitnum = 0#              int ;
                                chflag[0] = (asicdatabits[0+bitoffset] << 31)+ (asicdatabits[1+bitoffset]<<30)+ (asicdatabits[2+bitoffset]<<29)+ (asicdatabits[3+bitoffset]<<28)

                                if(asicdatabits[1+bitoffset] == 0):
                                    chflag[0] += (asicdatabits[4+bitoffset]<< 27)
                                    bitoffset += 5
                                else:
                                    chflag[0] += (asicdatabits[4+bitoffset]<<1)
                                    chflag[1] =0
                                    chflag[2] =0
                                    for l in range(noofch):
                                        if(l<32):
                                            chflag[1] += (asicdatabits[5+l+bitoffset] << (31-l))
                                        else:
                                            chflag[2] += (asicdatabits[5+l+bitoffset] << (63-l))
                                        if(asicdatabits[5+l+bitoffset]==1):
                                            #print(hitnum)
                                            index[hitnum] = l
                                            hitnum+=1

                                    chflag[0] += (asicdatabits[69+bitoffset])

                                    for l in range(10):
                                        ref += (asicdatabits[70+l+bitoffset] << l)
                                        for i in range(hitnum):
                                            adc[i] += (asicdatabits[80+10*i+l+bitoffset] << l)
                                        cmn += (asicdatabits[80+10*hitnum+l+bitoffset] << l)

                                    chflag[0] += (asicdatabits[80+10*hitnum+10+bitoffset]<< 27)
                                    bitoffset += (80+10*hitnum+10+1)

                                k= iasic + idchain * numofasicperdaisychains;
                                #print(k, iasic , idchain)

                                #if( not(eventid % 1000) and k==0):
                                    #print(eventid)
                                if(k==0):
                                    array_chflag=[]
                                    array_adccmn=[]
                                    array_index=[]
                                    array_cmn=[]

                                array_chflag.append([chflag[0],chflag[1],chflag[2]])
                                array_cmn_ex[k] =statistics.median(adc)
                                array_ref[k] = ref
                                array_hitnum[k] = hitnum

                                if(k==0):
                                    array_adccmn.append([])
                                    array_index.append([])
                                    array_cmn.append([])
                                    for i in range(hitnum):
                                        array_adccmn[0].append(adc[i]-cmn)
                                        array_index[0].append(index[i])
                                    array_cmn[0].append(cmn)

                                elif(k==1):
                                    for i in range(hitnum):
                                        array_adccmn[0].append(adc[i]-cmn)
                                        array_index[0].append(index[i]+64)
                                    array_cmn[0].append(cmn)
                                    if(array_hitnum[0]+array_hitnum[1]<noofch*2):
                                        for i in range(noofch*2-(array_hitnum[0]+array_hitnum[1])):
                                            array_adccmn[0].append(0)
                                            array_index[0].append(128)
                                    

                                elif(k==2):
                                    array_adccmn.append([])
                                    array_index.append([])
                                    array_cmn.append([])
                                    for i in range(hitnum):
                                        array_adccmn[1].append(adc[i]-cmn)
                                        array_index[1].append(index[i])
                                    array_cmn[1].append(cmn)

                                elif(k==3):
                                    for i in range(hitnum):
                                        array_adccmn[1].append(adc[i]-cmn)
                                        array_index[1].append(index[i]+64)
                                    array_cmn[1].append(cmn)
                                    if(array_hitnum[2]+array_hitnum[3]<noofch*2):
                                        for i in range(noofch*2-(array_hitnum[2]+array_hitnum[3])):
                                            array_adccmn[1].append(0)
                                            array_index[1].append(128)

                                #if (eventid == 1):
                                    #print(iasic,idchain,k,i, array_index,array_adccmn)

                                

                            if (bitoffset % 32 != 0):
                                bitoffset += (32 - bitoffset % 32)
                            bitoffset += 32
                    eventid+=1


                    hitnum_al = array_hitnum[2]+array_hitnum[3]
                    hitnum_pt = array_hitnum[0]+array_hitnum[1]

                    Lti.append(ti)
                    #print(unixtime)
                    Lunixtime.append(unixtime)
                    Llivetime.append(livetime)
                    Ladccmn_al.append(array_adccmn[1])
                    Ladccmn_pt.append(array_adccmn[0])
                    Lcmn_al.append(array_cmn[1])
                    Lcmn_pt.append(array_cmn[0])
                    Lindex_al.append(array_index[1])
                    Lindex_pt.append(array_index[0])
                    Lhitnum_al.append(hitnum_al)
                    Lhitnum_pt.append(hitnum_pt)
                    Lflag_pseudo.append(flag_pseudo)


    if(eventflag and hkflag):
        errorflag = True
        print("CAUTION!! : INPUT DATA IS FRAME DATA? BOTH HK AND EVENT DATA ARE FOUND")

    # # Example of Numpy structured array
    # >> dt = np.dtype({'names':('t',"y"),'formats':('(3,)f4', 'i4')})
    # >> data = np.zeros(3, dtype=dt)
    # >> data['t'] = np.array([[1,2,3],[4,5,6],[7,8,9]])
    # >> data['y'] = np.array([56,87,23])
    # >> data
    # array([([1., 2., 3.], 56), ([4., 5., 6.], 87), ([7., 8., 9.], 23)],
    #   dtype=[('t', '<f4', (3,)), ('y', '<i4')])

    evt_num = len(Lti)
    dt = np.dtype({'names':('ti', 'unixtime', 'livetime', 'adc_cmn_al', 'adc_cmn_pt', 'cmn_al', 'cmn_pt', 'index_al', 'index_pt', 'hitnum_al', 'hitnum_pt', 'flag_pseudo'),
                   'formats':('u4', 'u4', 'u4', '(128,)i4', '(128,)i4', '(2,)i4', '(2,)i4', '(128,)u1', '(128,)u1', 'u1', 'u1', 'u1')}) # u1==np.uint8,u4==np.uint32, i4==int32
    df = np.zeros(evt_num, dtype=dt)
    df['ti'] = np.array(Lti,dtype=np.uint32)
    df['unixtime'] = np.array(Lunixtime,dtype=np.uint32)
    df['livetime'] = np.array(Llivetime,dtype=np.uint32)
    df['adc_cmn_al'] = np.array(Ladccmn_al,dtype=np.int32)
    df['adc_cmn_pt'] = np.array(Ladccmn_pt,dtype=np.int32)
    df['cmn_al'] = np.array(Lcmn_al,dtype=np.uint32)
    df['cmn_pt'] = np.array(Lcmn_pt,dtype=np.uint32)
    df['index_al'] = np.array(Lindex_al,dtype=np.uint8)
    df['index_pt'] = np.array(Lindex_pt,dtype=np.uint8)
    df['hitnum_al'] = np.array(Lhitnum_al,dtype=np.uint8)
    df['hitnum_pt'] = np.array(Lhitnum_pt,dtype=np.uint8)
    df['flag_pseudo'] = np.array(Lflag_pseudo,dtype=np.uint8)

    flags=[hkflag,eventflag, errorflag]

    return flags,df,all_hkdicts



def CdTecanisterhkparser(data: bytes):
    error_flag = False
    frame_size = 816
    if len(data) % frame_size != 0:
        print("CdTecanisterhkparser() expects a input length to be a multiple of", frame_size)
        error_flag = True
        return [{},error_flag]
    
    # pull out data region for the DAQ parameters
    daq_data = data[0x18:0xf0]
    # pull out raw status bytes, frame data write pointer, and written frame counter
    status_raw          = data[0     :   0x0c]
    write_pointer_raw   = data[0x314 :   0x314+4]
    frame_count_raw     = data[0x318 :   0x318+4]
    unread_can_frame_count_raw  = data[0x32c :   0x32c+4]
    
    # all values from https://github.com/foxsi/CdTe_DE/blob/main/fig/DAQ_parameter_address.png
    daq_param_map = {
        "hv_exec":              int.from_bytes(daq_data[0x00 : 0x00+4], 'big'),
        "hv_set":               int.from_bytes(daq_data[0x04 : 0x04+4], 'big'),
        "data_copy_rate":       int.from_bytes(daq_data[0x08 : 0x08+4], 'big'),
        "pseudo_onoff0":        int.from_bytes(daq_data[0x0c : 0x0c+4], 'big'),
        "pseudo_rate0":         int.from_bytes(daq_data[0x10 : 0x10+4], 'big'),
        "va_status":            int.from_bytes(daq_data[0x20 : 0x20+4], 'big'),
        "module_status":        int.from_bytes(daq_data[0x24 : 0x24+4], 'big'),
        "enable_flag":          int.from_bytes(daq_data[0x38 : 0x38+4], 'big'),
        "extern_input_mode":    int.from_bytes(daq_data[0x3c : 0x3c+4], 'big'),
        "peaking_time":         int.from_bytes(daq_data[0x40 : 0x40+4], 'big'),
        "adc_clock_period":     int.from_bytes(daq_data[0x44 : 0x44+4], 'big'),
        "readout_period":       int.from_bytes(daq_data[0x48 : 0x48+4], 'big'),     # may also be readout delay??
        "trigpat_latch_timing": int.from_bytes(daq_data[0x54 : 0x54+4], 'big'),
        "reset_wait_time1":     int.from_bytes(daq_data[0x58 : 0x58+4], 'big'),
        "reset_wait_time2":     int.from_bytes(daq_data[0x5c : 0x5c+4], 'big'),
        "ti":                   int.from_bytes(daq_data[0x60 : 0x60+4], 'big'),
        "integral_livetime":    int.from_bytes(daq_data[0x64 : 0x64+4], 'big'),
        "deadtime":             int.from_bytes(daq_data[0x68 : 0x68+4], 'big'),
        "test_data":            int.from_bytes(daq_data[0x6c : 0x6c+4], 'big'),
        "cald_trigger_request": int.from_bytes(daq_data[0x70 : 0x70+4], 'big'),
        "ti_upper32":           int.from_bytes(daq_data[0x90 : 0x90+4], 'big'),
        "ti_lower32":           int.from_bytes(daq_data[0x94 : 0x94+4], 'big'),
        "ti_upper32_next":      int.from_bytes(daq_data[0x98 : 0x98+4], 'big'),
        "timecode":             int.from_bytes(daq_data[0x9c : 0x9c+4], 'big'),
        "ext1_ti_upper32":      int.from_bytes(daq_data[0xa0 : 0xa0+4], 'big'),
        "ext1_ti_lower32":      int.from_bytes(daq_data[0xa4 : 0xa4+4], 'big'),
        "ext2_ti_upper32":      int.from_bytes(daq_data[0xb0 : 0xb0+4], 'big'),
        "ext2_ti_lower32":      int.from_bytes(daq_data[0xb4 : 0xb4+4], 'big'),
        "pseudo_onoff1":        int.from_bytes(daq_data[0xc0 : 0xc0+4], 'big'),
        "pseudo_rate1":         int.from_bytes(daq_data[0xc4 : 0xc4+4], 'big'),
        "pseudo_counter":       int.from_bytes(daq_data[0xc8 : 0xc8+4], 'big'),
        "write_ptr":            int.from_bytes(daq_data[0xd0 : 0xd0+4], 'big'),
        "write_ptr_reset_req":  int.from_bytes(daq_data[0xd4 : 0xd4+4], 'big'),
    }

    # lookup status label by raw status bytes
    status_converter = {
        b"\x5a\x5a\x01\x00\x00\x00\x00\x00\x5a\x5a\x5a\x5a": "idle",
        b"\x5a\x5a\x01\x00\x01\x01\x01\x01\x5a\x5a\x5a\x5a": "started",
        b"\x5a\x5a\x01\x00\x01\x01\x00\x00\x5a\x5a\x5a\x5a": "started, reset pointer",
        b"\x5a\x5a\x01\x00\x02\x02\x02\x02\x5a\x5a\x5a\x5a": "stopped",
        b"\x5a\x5a\x01\x00\x03\x03\x00\x00\x5a\x5a\x5a\x5a": "HV = 0 V",
        b"\x5a\x5a\x01\x00\x03\x03\x01\x01\x5a\x5a\x5a\x5a": "HV = 60 V",
        b"\x5a\x5a\x01\x00\x03\x03\x02\x02\x5a\x5a\x5a\x5a": "HV = 100 V",
        b"\x5a\x5a\x01\x00\x03\x03\x03\x03\x5a\x5a\x5a\x5a": "HV = 200 V",
        b"\x5a\x5a\x01\x00\x06\x06\x06\x06\x5a\x5a\x5a\x5a": "DAQ param update",
        b"\x5a\x5a\x01\x00\x07\x07\x07\x07\x5a\x5a\x5a\x5a": "ASIC param update",
        b"\x5a\x5a\x01\x00\x05\x05\x05\x05\x5a\x5a\x5a\x5a": "ended"
    }

    status = ""
    try:
        status = status_converter[status_raw]
    except KeyError:
        print("Could not parse CdTe canister status")
        status = status_raw.hex()
        error_flag = True

    # convert raw write_pointer and frame_count to `int`
    write_pointer = int.from_bytes(write_pointer_raw, 'big')
    frame_count = int.from_bytes(frame_count_raw, 'big')
    unread_can_frame_count = int.from_bytes(unread_can_frame_count_raw, 'big')

    # convert raw high voltage DAC setting to voltage
    hv_set_converter = {
        0   : "0 V",
        1600: "60 V",
        2000: "100 V",
        3500: "200 V",
    }
    hv = hv_set_converter[daq_param_map["hv_set"]]

    # create output dict
    parsed_data = {
        "status": status,
        # "hv_exec": hv_exec,
        "hv": hv,
        "write_pointer": write_pointer,
        "frame_count": frame_count,
        "unread_can_frame_count": unread_can_frame_count
    }
    
    parsed_data.update(daq_param_map)

    return parsed_data, error_flag



def CdTedehkparser(data: bytes):
    error_flag = False
    frame_size = 32
    if len(data) % frame_size != 0:
        print("CdTecanisterhkparser() expects a input length to be a multiple of", frame_size)
        error_flag = True
        return [{},error_flag]
    
    status_raw      = data[0     :   0x0c]
    ping_raw        = data[0x0c  :   0x0c+4]
    temp_raw        = data[0x10  :   0x10+4]
    cpu_raw         = data[0x14  :   0x14+4]
    df_raw          = data[0x18  :   0x18+4]
    unixtime_raw    = data[0x1c  :   0x1c+4]

    # lookup status label by raw status bytes
    status_converter = {
        b"\x5a\x5a\x01\x00\x00\x00\x00\x00\x5a\x5a\x5a\x5a": "idle",
        b"\x5a\x5a\x01\x00\x01\x01\x01\x01\x5a\x5a\x5a\x5a": "init",
        b"\x5a\x5a\x01\x00\x02\x02\x02\x02\x5a\x5a\x5a\x5a": "standby",
        b"\x5a\x5a\x01\x00\x03\x03\x03\x03\x5a\x5a\x5a\x5a": "observe",
        b"\x5a\x5a\x01\x00\x04\x04\x04\x04\x5a\x5a\x5a\x5a": "end",
        b"\x5a\x5a\x01\x00\x07\x07\x07\x07\x5a\x5a\x5a\x5a": "ping update",
        b"\x5a\x5a\x01\x01\x01\x01\x01\x01\x5a\x5a\x5a\x5a": "broadcast start, pointer reset",
        b"\x5a\x5a\x01\x01\x01\x01\x02\x02\x5a\x5a\x5a\x5a": "broadcast start",
        b"\x5a\x5a\x01\x01\x02\x02\x02\x02\x5a\x5a\x5a\x5a": "broadcast stop",
        b"\x5a\x5a\x01\x01\x05\x05\x05\x05\x5a\x5a\x5a\x5a": "canisters stopped",
    }

    status = ""
    try:
        status = status_converter[status_raw]
    except KeyError:
        print("Could not parse CdTe canister status")
        status = status_raw.hex()
        error_flag = True

    ping = [can_ping for can_ping in ping_raw]
    temp = int.from_bytes(temp_raw, 'big')
    cpu = int.from_bytes(cpu_raw, 'big')
    df_GB = int.from_bytes(df_raw, 'big')
    unixtime = int.from_bytes(unixtime_raw, 'big')

    parsed_data = {
        "status": status,
        "ping": ping,
        "temp": temp,
        "cpu": cpu,
        "df_GB": df_GB,
        "unixtime": unixtime
    }

    return parsed_data, error_flag



if __name__ == "__main__":
    if len(sys.argv) > 2:
        with open(sys.argv[2], 'rb') as hk_file:
            data = hk_file.read()
            if "can" in sys.argv[1]:
                for i in range(0,len(data),0x31c):
                    print(i)
                    CdTecanisterhkparser(data[i:i+0x31c])
            elif "de" in sys.argv[1]:
                for i in range(0,len(data),0x20):
                    print(i)
                    CdTedehkparser(data[i:i+0x20])
            else:
                print("usage:\n>\tpython CdTeparser.py <cdtede | canister> path/to/hk/file.log")
    else:
        print("usage:\n\t> python CdTeparser.py <cdtede | canister> path/to/hk/file.log")