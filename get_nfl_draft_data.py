"""
  Get NFL Draft Data Script
  By Wilson Qin

  I wrote this script originally in September 2015
  to help a friend mine NFL Draft Data for statistical correlations.

  Usage:
    run: `python get_nfl_draft_data.py <player names file> <output file>`

    `--help` for further options
"""

import requests
import re

from bs4 import BeautifulSoup

import argparse

wiki_url = "https://en.wikipedia.org/wiki/"

_err = False


### some sample urls to test ###
# url = "https://en.wikipedia.org/wiki/Jackson_Jeffcoat"
# url2 = "https://en.wikipedia.org/wiki/Tyron_Smith"

  
"""
  constructor to generate a probable wikipedia url for a football player
  
  takes:
    football player plaintext name (string)
  returns:
    url (string)
"""
def make_wikipedia_url(playername, football_explicit=False):
  name_parts = playername.split(" ")
  fname = name_parts[0]
  lname = name_parts[1]

  suffix = ""

  if football_explicit:
    suffix += "_" + "(American_football)"

  return wiki_url + fname + "_" + lname + suffix


"""

"""
def get_draft_pick_for_player(playername):
  url = make_wikipedia_url(playername)

  r = requests.get(url, allow_redirects=True)

  soup = BeautifulSoup(r.text, 'html.parser')

  # search for disambiguation signs on the page
  if len(soup.find_all("a", title="Help:Disambiguation")) > 0:
    url = make_wikipedia_url(playername, football_explicit=True)
    r = requests.get(url, allow_redirects=True)
    soup = BeautifulSoup(r.text, 'html.parser')
    # TODO: currently there may be more disambiguation required

  # find nfl draft, if drafted
  results = soup.find_all("a", title=re.compile(".* NFL draft"))

  was_drafted = False
  rnd = None
  pck = None

  if len(results) <= 0:
    if not soup.find_all("a", title=re.compile("Undrafted")):
      return None

  for res in results:
    if res.next_sibling:
      # acquire the matched elements' html sibilings that hold NFL Draft info
      try:
        pick_parse = res.next_sibling.encode('ascii', 'ignore').decode('ascii').split("/")
      except:
        pick_parse = []

      try:
        if len(pick_parse) > 2:
          # Wikipedia convention seems to be of the format
          # NFL Draft / Round: 3 / Pick: 3
          # So isolate the numerical round and pick
          rnd = pick_parse[1].replace("Round", "").replace(":","").strip()
          pck = pick_parse[2].replace("Pick", "").replace(":","").strip()
          was_drafted = True

      except:
        if _err:
          print "Error parsing for", playername
          print pick_parse

        return [str(was_drafted), str(rnd), str(pck)]

  return [str(was_drafted), str(rnd), str(pck)]


def main():
  parser = argparse.ArgumentParser(description='Go to Wikipedia and fetch NFL Draft data on football players.')
  parser.add_argument('filename', metavar='F', type=argparse.FileType('r+'), nargs=1,
                     help='plain text file with player names separated by newlines.')
  parser.add_argument('outfile', metavar='O', type=argparse.FileType('w'), nargs=1,
                     help='csv file to write output data.')
  parser.add_argument('--skip', metavar='N', type=int,
                      default=0,
                      help='number of lines to skip when processing F. default is 0.')
  parser.add_argument('--verbose', metavar='V', type=bool, nargs='?', const=True, default=False,
                      help='verbose mode for error reporting.')

  args = parser.parse_args()

  f = args.filename[0]
  out = args.outfile[0]
  skip = args.skip
  _err = args.verbose

  # read a plain text file of player names
  # one plain text string per line.
  # opens the csv file
  names = f.read()
  f.close()

  # write csv header
  out.write("\t".join(["name", "was_drafted", "round", "pick"]) + "\n")

  for name in names.split("\n")[skip::]:
    draft_data = get_draft_pick_for_player(name)

    if draft_data:
      results = [name] + draft_data
      out.write("\t".join(results) + "\n")
      out.flush()
    else:
      # Control flow hitting here means either:
      # 1. player did not have a Wikipedia Page
      # 2. player needs further disambiguation by Football Position
      print "Unable to verify data for: ", name

  out.close()


main()
