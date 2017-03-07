import os, os.path
import sys
import pygtk
pygtk.require ('2.0')
import time
import gtk
if gtk.pygtk_version < (2,10,0):
    print "PyGtk 2.10 or later required for this example"
    raise SystemExit
import webbrowser
import gtksourceview2
import pango
from threading import Thread

######################################################################
##### global vars
windows = []    # this list contains all view windows
MARK_CATEGORY_1 = 'one'
MARK_CATEGORY_2 = 'two'
DATADIR = '/usr/share'
langu=""
pydata="# your code goes here"
cppdata="#include <iostream>\nusing namespace std;\nint main() {\n	// your code goes here\n	return 0;\n}"
javadata="import java.util.*;\nimport java.lang.*;\nimport java.io.*;\n\npublic class PreDefined\n{\n    public static void main (String[] args) throws java.lang.Exception\n    {\n        // your code goes here\n    }\n}"
htmldata="<html>\n    <head>\n        <title> Title goes here.... </title>\n    </head>\n    <body>\n        body goes here...\n    </body>\n</html>"
filenm=""
highlight=""
time_limit="5"
time_limit_exceed=False
time_count=0
######################################################################
##### error dialog
def error_dialog(parent, msg):
    dialog = gtk.MessageDialog(parent,
                               gtk.DIALOG_DESTROY_WITH_PARENT,
                               gtk.MESSAGE_ERROR,
                               gtk.BUTTONS_OK,
                               msg)
    dialog.run()
    dialog.destroy()
    

######################################################################
##### remove all markers
def remove_all_marks(buffer):
    begin, end = buffer.get_bounds()
    buffer.remove_source_marks(begin, end)


######################################################################
##### load file
def load_file(buffer, path):
    buffer.begin_not_undoable_action()
    try:
        txt = open(path).read()
    except:
        return False
    buffer.set_text(txt)
    buffer.set_data('filename', path)
    buffer.end_not_undoable_action()

    buffer.set_modified(False)
    buffer.place_cursor(buffer.get_start_iter())
    return True


######################################################################
##### buffer creation
def open_file(buffer, filename,py,cpp,java,html,other):
    # get the new language for the file mimetype
    manager = buffer.get_data('languages-manager')

    if os.path.isabs(filename):
        path = filename
    else:
        path = os.path.abspath(filename)
    global filenm
    filenm=filename
    
    language = manager.guess_language(filename)
    #print language
    filen, file_extension = os.path.splitext(filename)
    if file_extension==".py":
        py.set_active(True)
        buffer.set_highlight_syntax(True)
        buffer.set_language(language)
        #print buffer.get_language()
    elif file_extension==".cpp":
        cpp.set_active(True)
        buffer.set_highlight_syntax(True)
        buffer.set_language(language)
    elif file_extension==".java":
        java.set_active(True)
        buffer.set_highlight_syntax(True)
        buffer.set_language(language)
    elif file_extension==".html":
        html.set_active(True)
        buffer.set_highlight_syntax(True)
        buffer.set_language(language)

    else:
        other.set_active(True)
        if language:
            buffer.set_highlight_syntax(True)
            buffer.set_language(language)
        else:
            print 'No language found for file "%s"' % filename
            buffer.set_highlight_syntax(False)

    remove_all_marks(buffer)   
 
    load_file(buffer, path) # TODO: check return
    return True

def set_data(action,buffer,filename):
    manager = buffer.get_data('languages-manager')
    language = manager.guess_language(filename)
    if language:
        buffer.set_highlight_syntax(True)
        buffer.set_language(language)
        #print buffer.get_language()
    else:
        print 'No language found for file "%s"' % filename
        buffer.set_highlight_syntax(False)
    global langu
    langu=action.get_name()
    if langu == "python" :
        buffer.set_text(pydata)   
    if langu == "cpp" :
        buffer.set_text(cppdata)    
    if langu == "java" :
        buffer.set_text(javadata)
    if langu == "html" :
        buffer.set_text(htmldata)  
    if langu == "other":
        buffer.set_text("")
    remove_all_marks(buffer) 
######################################################################
##### Printing callbacks
def begin_print_cb(operation, context, compositor):
    while not compositor.paginate(context):
        pass
    n_pages = compositor.get_n_pages()
    operation.set_n_pages(n_pages)


def draw_page_cb(operation, context, page_nr, compositor):
    compositor.draw_page(context, page_nr)


######################################################################
##### Action callbacks

def open_file_cb(action, buffer,py,cpp,java,html,other):
    chooser = gtk.FileChooserDialog('Open file...', None,
                                    gtk.FILE_CHOOSER_ACTION_OPEN,
                                    (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                    gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    response = chooser.run()
    if response == gtk.RESPONSE_OK:
        filename = chooser.get_filename()
        if filename:
            open_file(buffer, filename,py,cpp,java,html,other)
    chooser.destroy()


def do_save(action, buffer,view,py,cpp,java,html,other):
    
    if filenm=="" :
        save_new_file_wo_cb(buffer,view,py,cpp,java,html,other)
    else :
        update_old_file(buffer)

def update_old_file(buffer):
    inp=buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter())
    iw=open(filenm,"wb")
    iw.write(inp)
    iw.close()

def save_new_file(action, buffer,view,py,cpp,java,html,other):
    save_new_file_wo_cb(buffer,view,py,cpp,java,html,other)

def save_new_file_wo_cb(buffer,view,py,cpp,java,html,other):
    chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                  buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
    file_check(chooser,buffer,view,py,cpp,java,html,other)

def file_check(chooser,buffer,view,py,cpp,java,html,other):
    response = chooser.run()
    
    if response == gtk.RESPONSE_OK:
        path = chooser.set_current_folder
        filename = chooser.get_filename()
        if os.path.exists(filename) :
            #replace=gtk.Button("Replace")
            duplicate=gtk.Dialog(title="File already exists",buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL))
            duplicate.add_button("Replace",gtk.RESPONSE_OK)
            label = gtk.Label("\nFile already exists.\n\nAre you sure you want to replace it ?\n")
            font_desc = pango.FontDescription('monospace 10')
            label.modify_font(font_desc)
            duplicate.vbox.pack_start(label)
            label.show()
            res=duplicate.run()
            if res == gtk.RESPONSE_OK:
                #res.destroy()
                chooser.destroy()
                replace_anyway(buffer,filename,py,cpp,java,html,other)
                duplicate.destroy() 
            else :
                duplicate.destroy()
                file_check(chooser,buffer,view,py,cpp,java,html,other)
        else :
            chooser.destroy()
            replace_anyway(buffer,filename,py,cpp,java,html,other)
    else:
        chooser.destroy()
   
def replace_anyway(buffer,filename,py,cpp,java,html,other):
    #chooser.destroy()
    if filename :
         #   filen=path+"/"+filename
        inp=buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter())
        iw=open(filename,"wb")
        iw.write(inp)
        iw.close()
        global filenm
        filenm=filename
        open_file(buffer, filename,py,cpp,java,html,other)



def numbers_toggled_cb(action, sourceview):
    sourceview.set_show_line_numbers(action.get_active())
    

def marks_toggled_cb(action, sourceview):
    sourceview.set_show_line_marks(action.get_active())
    
def auto_indent_toggled_cb(action, sourceview):
    sourceview.set_auto_indent(action.get_active())
    

def insert_spaces_toggled_cb(action, sourceview):
    sourceview.set_insert_spaces_instead_of_tabs(action.get_active())
    

def tabs_toggled_cb(action,buffer,  sourceview):
    
    sourceview.set_tab_width(int(action.get_name()))
    update_cursor_position(buffer, sourceview)

def time_limit_cb(action):
    global time_limit
    time_limit=action.get_name()
   
    if time_limit=="inf":
        global time_count
        time_count=time_count+1
        if time_count%2!=0:
            search=gtk.Dialog("Alert",buttons=(gtk.STOCK_CLOSE,gtk.RESPONSE_CANCEL))
            buffer1 = gtksourceview2.Buffer()
       
            label1=gtk.Label("We do not recommend this option.")
            label2=gtk.Label("No time limit option can hang the editor in cases like infinite loop.")
            label3=gtk.Label("Atleast save your work before you give 'run' command")
            search.vbox.pack_start(label1,True,True,4)
            label1.show()
            search.vbox.pack_start(label2,True,True,4)
            label2.show()
            search.vbox.pack_start(label3,True,True,4)
            label3.show()
            search.run()
            search.destroy()


def new_view_cb(action):
    lm = gtksourceview2.LanguageManager()
    buffer = gtksourceview2.Buffer()

    buffer1 = gtksourceview2.Buffer()
    buffer2 = gtksourceview2.Buffer()

    buffer.set_data('languages-manager', lm)
    
    
    window = create_view_window(buffer,buffer1,buffer2)
    window.set_default_size(400, 400)
    window.show()

######################################################################
##### Buffer action callbacks

def update_cursor_position(buffer, view):
    tabwidth = view.get_tab_width()
    pos_label = view.get_data('pos_label')
    iter = buffer.get_iter_at_mark(buffer.get_insert())
    nchars = iter.get_offset()
    row = iter.get_line() + 1
    start = iter.copy()
    start.set_line_offset(0)
    col = 0
    while start.compare(iter) < 0:
        if start.get_char() == '\t':
            col += tabwidth - col % tabwidth
        else:
            col += 1
        start.forward_char()
    pos_label.set_text('char: %d, line: %d, column: %d' % (nchars, row, col+1))
    

def move_cursor_cb (buffer, cursoriter, mark, view):
    update_cursor_position(buffer, view)


def window_deleted_cb(widget, ev, view):
    
    windows.remove(widget)
   
    if len(windows)==0:
        gtk.main_quit()
        
    return False


def button_press_cb(view, ev):
    buffer = view.get_buffer()
    if not view.get_show_line_marks():
        return False
    # check that the click was on the left gutter
    if ev.window == view.get_window(gtk.TEXT_WINDOW_LEFT):
        if ev.button == 1:
            mark_category = MARK_CATEGORY_1
        else:
            mark_category = MARK_CATEGORY_2
        x_buf, y_buf = view.window_to_buffer_coords(gtk.TEXT_WINDOW_LEFT,
                                                    int(ev.x), int(ev.y))
        # get line bounds
        line_start = view.get_line_at_y(y_buf)[0]

        # get the markers already in the line
        mark_list = buffer.get_source_marks_at_line(line_start.get_line(), mark_category)
        # search for the marker corresponding to the button pressed
        for m in mark_list:
            if m.get_category() == mark_category:
                # a marker was found, so delete it
                buffer.delete_mark(m)
                break
        else:
            # no marker found, create one
            buffer.create_source_mark(None, mark_category, line_start)
    
    return False
elapsed_time=0
def python_run():
    global time_limit_exceed
    time_limit_exceed=True
    start_time=time.time()
    os.system("python deepanshu.py < input > output 2> error")
    global elapsed_time
    elapsed_time=time.time()-start_time
    time_limit_exceed=False

def cpp_run():
    global time_limit_exceed
    time_limit_exceed=True
    start_time=time.time()
    os.system("./a.out < input >output 2> error")
    global elapsed_time    
    elapsed_time=time.time()-start_time
    time_limit_exceed=False

def java_run():
    global time_limit_exceed
    time_limit_exceed=True
    start_time=time.time()
    os.system("java PreDefined < input >output 2> error")
    global elapsed_time
    elapsed_time=time.time()-start_time
    time_limit_exceed=False

def faltu(buffer2):
    buffer2.set_text("")
    #run_cb(buffer,buffer1,buffer2,view2)

def run_cb(action,buffer,buffer1,buffer2,view2):
    #t7=Thread(target=faltu(buffer2))
    #t7.start()
    #t7.join()
    data=buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter())
    inp=buffer1.get_text(buffer1.get_start_iter(),buffer1.get_end_iter())
    tx=open("input","wb")
    tx.write(inp)
    tx.close()
    outdata=""
    #buffer2.set_text("hi")
    global elapsed_time
    need_thread=True
    limit=0
    if time_limit=="inf":
        need_thread=False
    else :
        limit=float(time_limit)
   
    if langu=="python" :
        fw=open("deepanshu.py","wb")
        fw.write(data)
        fw.close()
        if need_thread:
            t1 = Thread(target=python_run)
            t1.setDaemon(True)
            t1.start()
            t1.join(limit)
            print t1.is_alive()
        else:
            python_run()
            
        dmy=open("error","r+")
        dmy1=dmy.read()
        dmy.write("")
        dmy.close()
        if(len(dmy1)>0):
            outdata="Error\n----------------------\n"+dmy1
            
            view2.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('#FF0000'))
        else:
            fow=open("output","r")
            #outdata=fow.read(50000)
            #fow.write("")
            #fow.close()
            if time_limit_exceed:
                outdata=fow.read()
                outdata="Time taken exceeded "+"\n----------------------\n"+outdata
                view2.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('#786D5F'))
            else:
                outdata=fow.read()
                outdata="Time taken : "+str(elapsed_time)[:5]+" seconds\n----------------------\n"+outdata
                view2.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('#008000'))
            fow.close()

    elif langu=="cpp":
        fw=open("deepanshu.cpp","wb")
        fw.write(data)
        fw.close()
        os.system("g++ deepanshu.cpp >output1 2>&1")
        ow=open("output1","r+")
        dmy=ow.read()
        ow.write("")
        ow.close()
        if(len(dmy)<=0):
            if need_thread:
                t1 = Thread(target=cpp_run)
                t1.setDaemon(True)
      
                t1.start()
       
                t1.join(limit)
            else:
                cpp_run()
            
            dmy1=open("error","r+")
            dmy2=dmy1.read()
            dmy1.write("")
            dmy1.close()
            if(len(dmy2)>0):
                outdata="Runtime Error\n----------------------\n"+dmy2
            
                view2.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('#FF0000'))
            else:
                fow=open("output","r")
                outdata=fow.read()
                #fow.write("")
                fow.close()
                if time_limit_exceed:
                    outdata="Time taken exceeded "+"\n----------------------\n"+outdata
                    view2.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('#786D5F'))
                else:
                    outdata="Time taken : "+str(elapsed_time)[:5]+" seconds\n----------------------\n"+outdata
                    view2.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('#008000'))
        else:
            outdata="Compilation Error\n----------------------\n"+dmy
            
            view2.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('#0000FF'))
       
    elif langu=="html":
        of=open("deepanshu.html","wb")
        of.write(data)
        of.close()
        x=os.getcwd()
        y="file://"+x+"/deepanshu.html"
        webbrowser.get("firefox").open(y)
      
    elif langu=="java":
        fw=open("PreDefined.java","wb")
        fw.write(data)
        fw.close()
        os.system("javac PreDefined.java > output1 2>&1")
        ow=open("output1","r+")
        dmy=ow.read()
        ow.write("")
        ow.close()
        if(len(dmy)<=0):
            if need_thread:
                t1 = Thread(target=java_run)
                t1.setDaemon(True)
       
                t1.start()
       
                t1.join(limit)
            else:
                java_run()
            
            dmy1=open("error","r+")
            dmy2=dmy1.read()
            dmy1.write("")
            dmy1.close()
            if(len(dmy2)>0):
                outdata="Runtime Error\n----------------------\n"+dmy2
                
                view2.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('#FF0000'))
            else:
                fow=open("output","r")
                outdata=fow.read()
                #fow.write("")
                fow.close()
                if time_limit_exceed:
                    outdata="Time taken exceeded "+"\n----------------------\n"+outdata
                    view2.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('#786D5F'))
                else:
                    outdata="Time taken : "+str(elapsed_time)[:5]+" seconds\n----------------------\n"+outdata
                    view2.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('#008000'))
                
        else:
            outdata="Compilation Error\n----------------------\n"+dmy
 
            view2.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('#0000FF'))
      
    buffer2.set_text(outdata)
    #os.remove("output")
    #fw=open("output","wb")
    #fw.write("")
    #fw.close()

def replace_all_cb(action,buffer):
    search=gtk.Dialog("Replace All",buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL))
    buffer1 = gtksourceview2.Buffer()
    search_text = gtksourceview2.View(buffer1)
    label=gtk.Label("Replace : ")
    search.vbox.pack_start(label,True,True,4)

    search.vbox.pack_start(search_text,True,True,4)
    label1=gtk.Label("")
    search.vbox.pack_start(label1,True,True,4)
    label1.show()


    buffer2 = gtksourceview2.Buffer()
    search_text2 = gtksourceview2.View(buffer2)
    label2=gtk.Label("Replace With : ")
    search.vbox.pack_start(label2,True,True,4)

    search.vbox.pack_start(search_text2,True,True,4)
    label3=gtk.Label("")
    search.vbox.pack_start(label3,True,True,4)
    label3.show()

    search.add_button("Replace All",gtk.RESPONSE_OK)
    
    search_text.show()
    search_text2.show()
    label.show()
    label2.show()
    run=search.run()
    search.destroy()
    if run == gtk.RESPONSE_OK :
            
            to_search=buffer1.get_text(buffer1.get_start_iter(),buffer1.get_end_iter())
            to_search2=buffer2.get_text(buffer2.get_start_iter(),buffer2.get_end_iter())
            
            replace_func(to_search,to_search2,buffer,buffer1,buffer2)


def replace_func(search_text,search_text2,buffer,buffer1,buffer2):
    if search_text == "" :
        return
    data=buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter())
    
    
    length=len(search_text)
    length2=len(data)
    if length2 < length :
        return
    x=0
    pos=0
    prev=0
    edit=""
    
    x=data.find(search_text,pos)
    if x!=-1:
        edit=data[0:x]+search_text2
        pos=x+length
        prev=x
    else:
        pos=length2
        edit=edit+data[prev:]
    
    while pos<length2:
        x=data.find(search_text,pos)
        if x!= -1 :
            edit=edit+data[prev+length:x]+search_text2
           # print buffer.get_text(start,end)
            pos=x+length
            prev=x
        else :
            pos=length2
            edit=edit+data[prev+length:]
    buffer.set_text(edit)
    search_func(search_text2,buffer)





def find_cb(action,buffer):
    search=gtk.Dialog("Find",buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL))
    buffer1 = gtksourceview2.Buffer()
    search_text = gtksourceview2.View(buffer1)
    label=gtk.Label("Search Text : ")
    search.vbox.pack_start(label,True,True,4)

    search.vbox.pack_start(search_text,True,True,4)

    case=gtk.CheckButton("Match Case")
    
    case.show()
    search.vbox.pack_start(case,True,True,4)
    search.add_button("Search",gtk.RESPONSE_OK)
    
    search_text.show()
    label.show()
    run=search.run()
    search.destroy()
    if run == gtk.RESPONSE_OK :
            #buffer1=search_text.get_buffer()
            to_search=buffer1.get_text(buffer1.get_start_iter(),buffer1.get_end_iter())
            #print to_search
            search_func(to_search,buffer,case.get_active())

def search_func(search_text,buffer,case=True):
    if search_text == "" :
        return
    data=buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter())
    if not case:
        search_text=search_text.lower()
        data=data.lower()
    buffer.remove_tag_by_name("highlight",buffer.get_start_iter(),buffer.get_end_iter())
    length=len(search_text)
    length2=len(data)
    if length2 < length :
        return
    x=0
    pos=0
    prev=0
    start=buffer.get_start_iter()
    end=buffer.get_start_iter()
    end.forward_chars(length)
    
    while pos<length2:
        x=data.find(search_text,pos)
        if x!= -1 :
            
            start.forward_chars(x-prev)
            end.forward_chars(x-prev)
            
            buffer.apply_tag(highlight,start,end)
            
            pos=x+length
            prev=x
        else :
            pos=length2

def non_highlight(action,buffer):
    buffer.remove_tag_by_name("highlight",buffer.get_start_iter(),buffer.get_end_iter())

######################################################################
##### create view window
def create_view_window(buffer,buffer1,buffer2, sourceview=None):
    # window
    
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.set_border_width(0)
    window.set_title('Multi Language Compiler')
    windows.append(window) # this list contains all view windows
    window.set_icon_from_file('icon.png')

    # view
    view = gtksourceview2.View(buffer)
    buffer.connect('mark_set', move_cursor_cb, view)
    buffer.connect('changed', update_cursor_position, view)
    view.connect('button-press-event', button_press_cb)
    window.connect('delete-event', window_deleted_cb, view)

    view1 = gtksourceview2.View(buffer1)
    view2 = gtksourceview2.View(buffer2)
    view2.set_editable(False)


    mb = gtk.MenuBar()

    filemenu = gtk.Menu()
    viewmenu = gtk.Menu()
    filem = gtk.MenuItem("_File")
    viewm = gtk.MenuItem("_View")
    filem.set_submenu(filemenu)
    viewm.set_submenu(viewmenu)
       
    agr = gtk.AccelGroup()
    window.add_accel_group(agr)
    

    newi = gtk.ImageMenuItem(gtk.STOCK_NEW, agr)
    key, mod = gtk.accelerator_parse("<Control>N")
    newi.add_accelerator("activate", agr, key, 
        mod, gtk.ACCEL_VISIBLE)
    #print sourceview
        #print "k"
    newi.connect("activate", new_view_cb)
    filemenu.append(newi)

    openm = gtk.ImageMenuItem(gtk.STOCK_OPEN, agr)
    key, mod = gtk.accelerator_parse("<Control>O")
    openm.add_accelerator("activate", agr, key, 
        mod, gtk.ACCEL_VISIBLE)
    #openm.connect("activate",open_file_cb,buffer)
    filemenu.append(openm)

    savem = gtk.ImageMenuItem(gtk.STOCK_SAVE, agr)
    filemenu.append(savem)
    saveasm = gtk.ImageMenuItem(gtk.STOCK_SAVE_AS, agr)
    key, mod = gtk.accelerator_parse("<Control><Shift>S")
    saveasm.add_accelerator("activate", agr, key, 
        mod, gtk.ACCEL_VISIBLE)
    filemenu.append(saveasm)
    
    sep = gtk.SeparatorMenuItem()
    filemenu.append(sep)

    exit = gtk.ImageMenuItem(gtk.STOCK_QUIT, agr)
    key, mod = gtk.accelerator_parse("<Control>Q")
    exit.add_accelerator("activate", agr, key, 
        mod, gtk.ACCEL_VISIBLE)

    exit.connect("activate", gtk.main_quit)
        
    showlinenumbers=gtk.CheckMenuItem("show line numbers")
    showlinenumbers.connect("activate",numbers_toggled_cb,view)
    viewmenu.append(showlinenumbers)

    showmarkers=gtk.CheckMenuItem("show markers")
    showmarkers.connect("activate",marks_toggled_cb,view)
    viewmenu.append(showmarkers)

    enableautoindent=gtk.CheckMenuItem("enable auto indent")
    enableautoindent.connect("activate",auto_indent_toggled_cb,view)
    viewmenu.append(enableautoindent)

    insertspacesinsteadoftabs=gtk.CheckMenuItem("insert spaces instead of tabs")
    insertspacesinsteadoftabs.connect("activate",insert_spaces_toggled_cb,view)
    viewmenu.append(insertspacesinsteadoftabs)

    tabmenu = gtk.Menu()
    tabm = gtk.MenuItem("_Tabs__Width")
    tabm.set_submenu(tabmenu)
    

    optionmenu = gtk.Menu()
    optionm = gtk.MenuItem("_Options")
    optionm.set_submenu(optionmenu)
    find=gtk.ImageMenuItem(gtk.STOCK_FIND,agr)
    
    optionmenu.append(find)
    find.connect("activate",find_cb,buffer)
    replace_all=gtk.MenuItem("Replace All",agr)
    key, mod = gtk.accelerator_parse("<Control>H")
    replace_all.add_accelerator("activate", agr, key, 
        mod, gtk.ACCEL_VISIBLE)
    optionmenu.append(replace_all)
    replace_all.connect("activate",replace_all_cb,buffer)
    unhighlight=gtk.MenuItem("Clear highlight")
    optionmenu.append(unhighlight)
    unhighlight.connect("activate",non_highlight,buffer)


    langmenu = gtk.Menu()
    langm = gtk.MenuItem("_Languages")
    langm.set_submenu(langmenu)

    py=gtk.RadioMenuItem(None,"Python")
    langmenu.append(py)
    py.connect("activate",set_data,buffer,"deepanshu.py")
    cpp=gtk.RadioMenuItem(py,"C++")
    langmenu.append(cpp)
    cpp.connect("activate",set_data,buffer,"deepanshu.cpp")
    java=gtk.RadioMenuItem(py,"Java")
    langmenu.append(java)
    java.connect("activate",set_data,buffer,"PreDefined.java")
    py.set_name("python")
    cpp.set_name("cpp")
    java.set_name("java")
    html=gtk.RadioMenuItem(py,"Html")
    langmenu.append(html)
    html.connect("activate",set_data,buffer,"deepanshu.html")
    html.set_name("html")
    runmenu=gtk.Menu()
    runm=gtk.MenuItem("_Run")
    runm.set_submenu(runmenu)
    run=gtk.MenuItem("run")
    other=gtk.RadioMenuItem(py,"other")
    langmenu.append(other)
    other.connect("activate",set_data,buffer,"deepanshu")
    other.set_name("other")

    openm.connect("activate",open_file_cb,buffer,py,cpp,java,html,other)    
    savem.connect("activate", do_save,buffer,view,py,cpp,java,html,other)
    saveasm.connect("activate", save_new_file,buffer,view,py,cpp,java,html,other)
    runmenu.append(run)
    key, mod = gtk.accelerator_parse("<Control>R")
    #run.set_accel_group(mod)
    run.add_accelerator("activate", agr, key, 
        mod, gtk.ACCEL_VISIBLE)
    run.connect("activate",run_cb,buffer,buffer1,buffer2,view2)
    #run.connect("activate",faltu,buffer2)
    #group=gtk.RadioMenuItem()

    timemenu = gtk.Menu()
    timem = gtk.MenuItem("_Time_Limit")
    timem.set_submenu(timemenu)
    time5=gtk.RadioMenuItem(None,"5 sec")
    timemenu.append(time5)
    time10=gtk.RadioMenuItem(time5,"10 sec")
    timemenu.append(time10)
    time15=gtk.RadioMenuItem(time5,"15 sec")
    timemenu.append(time15)
    notime=gtk.RadioMenuItem(time5,"no limit")
    timemenu.append(notime)
    time5.set_name("5")
    time5.connect("activate",time_limit_cb)
    time10.set_name("10")
    time10.connect("activate",time_limit_cb)
    time15.set_name("15")
    time15.connect("activate",time_limit_cb)
    notime.set_name("inf")
    notime.connect("activate",time_limit_cb)
    

    tab2=gtk.RadioMenuItem(None,"2")
    tabmenu.append(tab2)
    tab4=gtk.RadioMenuItem(tab2,"4")
    tabmenu.append(tab4)
    tab6=gtk.RadioMenuItem(tab2,"6")
    tabmenu.append(tab6)
    tab8=gtk.RadioMenuItem(tab2,"8")
    tabmenu.append(tab8)
    tab10=gtk.RadioMenuItem(tab2,"10")
    tabmenu.append(tab10)
    tab12=gtk.RadioMenuItem(tab2,"12")
    tabmenu.append(tab12)
    tab2.set_name("2")
    tab2.connect("activate",tabs_toggled_cb,buffer,view)
    tab4.set_name("4")
    tab4.connect("activate",tabs_toggled_cb,buffer,view)
    tab8.set_name("8")
    tab8.connect("activate",tabs_toggled_cb,buffer,view)
    tab6.set_name("6")
    tab6.connect("activate",tabs_toggled_cb,buffer,view)
    tab10.set_name("10")
    tab10.connect("activate",tabs_toggled_cb,buffer,view)
    tab12.set_name("12")
    tab12.connect("activate",tabs_toggled_cb,buffer,view)
    


    filemenu.append(exit)

    mb.append(filem)
    mb.append(viewm)
   # mb.append(tabm)
    mb.append(langm)
    mb.append(optionm)
    mb.append(runm)
    mb.append(timem)
    mb.append(tabm)
    # misc widgets
    vbox = gtk.VBox(0, False)
    sw = gtk.ScrolledWindow()
    sw.set_shadow_type(gtk.SHADOW_IN)
    pos_label = gtk.Label('Position')
    view.set_data('pos_label', pos_label)
    
    
    sw1 = gtk.ScrolledWindow()
    sw2 = gtk.ScrolledWindow()


    # layout widgets
    window.add(vbox)
    vbox.pack_start(mb, False, False, 0)


    

    table = gtk.Table(20, 5, True)
    table.attach(sw,0,3,1,20)
    table.attach(gtk.Label("Code goes here ...."), 0, 3, 0, 1)
    table.attach(sw1,3,5,1,10)
    table.attach(gtk.Label("Input"), 3, 5, 0, 1)
    table.attach(sw2,3,5,11,20)
    table.attach(gtk.Label("Output"), 3, 5, 10, 11)




    vbox.pack_start(table, True, True, 0)
    sw.add(view)
    vbox.pack_start(pos_label, False, False, 0)

    sw1.add(view1)
    #vbox.pack_start(sw1, True, True, 0)
    
    sw2.add(view2)

    # setup view
    font_desc = pango.FontDescription('monospace 10')
    if font_desc:
        view.modify_font(font_desc)
        view1.modify_font(font_desc)
        view2.modify_font(font_desc)
    
    vbox.show_all()
    time5.set_active(True)
    tab4.set_active(True)
    showlinenumbers.set_active(True)
    showmarkers.set_active(True)
    enableautoindent.set_active(True)
    py.set_active(True)
    return window
    
    
######################################################################
##### main
def main(args):
    # create buffer
    lm = gtksourceview2.LanguageManager()
    buffer = gtksourceview2.Buffer()
    global highlight
    highlight=buffer.create_tag("highlight",background="#FFFF00")
    buffer1 = gtksourceview2.Buffer()
    buffer2 = gtksourceview2.Buffer()

    buffer.set_data('languages-manager', lm)
    # create first window
    window = create_view_window(buffer,buffer1,buffer2)
    window.set_default_size(500, 500)
    window.show()

    # main loop
    gtk.main()
    

if __name__ == '__main__':
    if '--debug' in sys.argv:
        import pdb
        pdb.run('main(sys.argv)')
    else:
        main(sys.argv)
