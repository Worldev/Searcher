#!/usr/bin/python3
"""
   Searcher
   Copyright © 2016 Miquel Comas (Mikicat) & Worldev
   
   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 3 of the License, or
   (at your option) any later version.
   
   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
   
   You should have received a copy of the GNU General Public License along
   with this program; if not, write to the Free Software Foundation, Inc.,
   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
from tkinter import *
from tkinter.filedialog import *
from tkinter.messagebox import *
from html.parser import HTMLParser
from html.entities import name2codepoint
import webbrowser
import urllib, urllib.parse, urllib.request
import json
try:
    import requests
except ImportError:
    print("Error: requests module not installed. Please install it with pip install requests")


class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print("Encountered a start tag:", tag)
    def handle_endtag(self, tag):
        print("Encountered an end tag :", tag)
    def handle_data(self, data):
        print("Encountered some data  :", data)
    
class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('Searcher / Buscador')
        self.master.resizable(0, 0)
        self.setup(master)
        
    def setup(self, master):
        self.label = Label(master, text='Search:').grid(row=0, column=0)
        self.lablang = Label(master, text='Language Code (e.g. en, es, ca):').grid(row=0, column=1)
        self.query = Entry(master)
        self.query.grid(row=1)
        self.lang = Entry(master)
        self.lang.grid(row=1, column=1)
        self.btn = Button(master, text='OK', command=self.getquery)
        self.btn.grid(row=2, column=2, sticky=W)
        self.close = Button(master, text='Close', command=exit).grid(row=4, column=0, sticky=W)        
        self.tex = Text(master)
        self.tex.grid(row=3, column=0)
        
    def getquery(self):
        if self.query.get() != '' or self.lang.get() != '':
            self.tex.delete('1.0', END)
            self.checkquery()
        else:
            showwarning("Alert!", "You have left some fileds empty")

    def checkquery(self):
        try:
            check_wikipedia = requests.get('https://' + self.lang.get() + '.wikipedia.org/wiki/' + self.query.get())

            if check_wikipedia.status_code == 200:
                self.wikipedia(self.lang.get(), self.query.get())
            else:
                self.tex.insert(END, 'This query doesn\'t have an article in Wikipedia\n')
                self.tex.see(END)
            self.search(self.query.get())
        except requests.exceptions.InvalidURL:
            showerror("Error!", "You cannot live the language code empty")


    def search(self, search_string):
        """Search a query to Google"""
        query = urllib.parse.urlencode({'q': search_string})
        url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s&rsz=large' % query
        search_response = urllib.request.urlopen(url)
        search_results = search_response.read().decode("utf8")
        results = json.loads(search_results)
        data = results['responseData']
        self.tex.insert(END, 'Total results: %s' % data['cursor']['estimatedResultCount'] + "\n")
        self.tex.see(END)
        hits = data['results']
        self.tex.insert(END, 'Top %d hits:' % len(hits))
        self.tex.see(END)
        for h in hits:
            self.tex.insert(END, ' ' + h['titleNoFormatting'] + "\n")
            self.tex.see(END)
            self.tex.insert(END, ' ' + h['url'] + "\n")
            self.tex.see(END)
            self.tex.insert(END, ' ' + h['content'] + "\n")
            self.tex.see(END)
            
        self.tex.insert(END, 'For more results, see %s' % data['cursor']['moreResultsUrl'] + "\n")
        self.tex.see(END)
        return hits

    def w_search(self, lang, query):
        url = 'https://%s.wikipedia.org/w/api.php?action=query&titles=%s&format=json&prop=extracts&exintro&explaintext&redirects' % (lang, query)
        search_response = urllib.request.urlopen(url)
        search_results = search_response.read().decode("utf8")
        snippet = json.loads(search_results)
        snippet = snippet['query']['pages']
        id = str(list(snippet.keys())[0])
        snippet = snippet[id]
        return snippet['extract']

    def wikipedia(self, lang, query):
        """Search a query to Wikipedia"""
        Label(self.master, text="Wikipedia article summary:").grid(row=2, column=3)
        self.tex2 = Text(self.master)
        self.tex2.grid(row=3, column=3)
        try:
            ws = self.w_search(lang, query)
            self.tex2.insert(END, ws)
            self.tex2.see(END)
        except Exception as e:
            self.tex2.insert(END, e)
            self.tex2.see(END)
        self.save_info = Button(self.master, text="See Wikipedia Article", command=self.see).grid(row=4, column=3)

    def see(self):
        webbrowser.open('https://%s.wikipedia.org/wiki/%s' % (self.lang.get(), self.query.get()))

            

root = Tk()
app = Application(master=root)
app.mainloop()

