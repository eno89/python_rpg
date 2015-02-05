
http://home.wlu.edu/~levys/software/kbhit.py

http://support.microsoft.com/kb/99261/ja

ar = [14, 665, 807, 878]
ar = [16,146,670,929,1028]
br = []
for e in range(len(ar)-1):
	br.append(ar[e+1] - ar[e])

br[-1] += ar[0]
for e in br: print "%4d  %3.1f" % (e, e * 100.0/ar[-1])

Map をつくる
アイテムは個人持ち
+共有

http://lightson.dip.jp/zope/ZWiki/267_e6_96_87_e5_ad_97_e5_88_97_e3_82_92Python_e3_82_b9_e3_82_af_e3_83_aa_e3_83_97_e3_83_88_e3_81_a8_e3_81_97_e3_81_a6_e5_ae_9f_e8_a1_8c_e3_81_99_e3_82_8b

exec 文を用います。現在のスコープ内で実行されます。

>>> exec '''def hello():
...   return 'Hello World.'
... '''
>>> hello()
'Hello World.'
閉じた環境を用意する場合 in を用います。

>>> G = {}
>>> L = {}
>>> exec '''def hello():
...   return 'Hello World.'
... ''' in G, L
>>> hello()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: name 'hello' is not defined
>>> L['hello']()
'Hello World.'
なお、文字列をスクリプトではなく「文」単体として評価するには eval 関数を用います。

>>> x = 1
>>> eval('x + 1')
2

http://d.hatena.ne.jp/yatt/20101122/1290430023

curses は unicode x 日本語ダメなので
pykbhit.py を借りる
