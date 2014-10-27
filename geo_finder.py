#! /usr/bin/env python

"""
Map a pair of coordinates to a unique city, or return None if no valid city is found
"""


import sys
import itertools
import math
try:
    import ujson as json
except ImportError:
    import json
import os


grid_size = 0.5 #measured by degree
earth_radius = 6372.8

def calc_dist_radian(pLat, pLon, lat, lon):
    cos_pLat = math.cos(pLat)
    sin_pLat = math.sin(pLat)
    cos_lat = math.cos(lat)
    sin_lat = math.sin(lat)
    long_diff = pLon - lon
    cos_long_diff = math.cos(long_diff)
    sin_long_diff = math.sin(long_diff)
    numerator = math.sqrt( math.pow(cos_lat * sin_long_diff, 2)+ math.pow(cos_pLat * sin_lat - sin_pLat * cos_lat * cos_long_diff, 2))
    denominator = sin_pLat*sin_lat + cos_pLat*cos_lat*cos_long_diff
    radian = math.atan2(numerator, denominator)
    return radian * earth_radius

def calc_dist_degree(pLat, pLon, lat, lon):
    pLat = degree_radian(pLat)
    pLon = degree_radian(pLon)
    lat = degree_radian(lat)
    lon = degree_radian(lon)
    return calc_dist_radian(pLat, pLon, lat, lon)

def degree_radian(degree):
    return (degree * math.pi)/180

def load_city_info():
    """    Get city information    """
    city_collapsed_all = """
bissau-11-gw	africa/bissau	11.86357	-15.59767	388028
chimaltenango-03-gt	america/guatemala	14.66861	-90.81667	194701
quetzaltenango-13-gt	america/guatemala	14.83333	-91.51667	283584
escuintla-06-gt	america/guatemala	14.305	-90.785	239247
guatemala city-07-gt	america/guatemala	14.64072	-90.51327	2653501
solola-19-gt	america/guatemala	14.76667	-91.18333	106372
huehuetenango-08-gt	america/guatemala	15.31972	-91.47083	113510
totonicapan-21-gt	america/guatemala	14.91667	-91.36667	155966
antigua guatemala-16-gt	america/guatemala	14.56111	-90.73444	183481
chichicastenango-14-gt	america/guatemala	14.93333	-91.11667	103377
thessaloniki-esye1213-gr	europe/athens	40.64028	22.94389	617451
athens-esye31-gr	europe/athens	37.97945	23.71622	2692146
larisa-esye1421-gr	europe/athens	39.63722	22.42028	128758
piraeus-esye3135-gr	europe/athens	37.94745	23.63708	172429
irakleion-esye4345-gr	europe/athens	35.32787	25.14341	137154
patra-esye2338-gr	europe/athens	38.24444	21.73444	184024
bata-08-gq	africa/malabo	1.86391	9.76582	173046
malabo-04-gq	africa/malabo	3.75	8.78333	155963
les abymes-gp971-gp	america/guadeloupe	16.27095	-61.50451	262601
georgetown-12-gy	america/guyana	6.80448	-58.15527	235017
cayenne-gf973-gf	america/cayenne	4.93333	-52.33333	130958
zugdidi-71-ge	asia/tbilisi	42.5088	41.87088	147907
bat'umi-04-ge	asia/tbilisi	41.64159	41.63593	140406
tbilisi-51-ge	asia/tbilisi	41.69411	44.83368	1049498
k'ut'aisi-66-ge	asia/tbilisi	42.24961	42.69974	220965
city of london-enggla-gb	europe/london	51.51279	-0.09184	17401356
cumbernauld-sctv8-gb	europe/london	55.94685	-3.99051	155910
high wycombe-engb9-gb	europe/london	51.62907	-0.74934	303185
bristol-engb7-gb	europe/london	51.45523	-2.59665	430713
bradford-engb4-gb	europe/london	53.79391	-1.75206	385518
bracknell-engb3-gb	europe/london	51.41363	-0.75054	101625
bournemouth-engb2-gb	europe/london	50.72048	-1.8795	163600
bolton-engb1-gb	europe/london	53.58333	-2.43333	183021
glasgow-sctv2-gb	europe/london	55.86515	-4.25763	610268
harrogate-engj7-gb	europe/london	53.99078	-1.5373	136498
wolverhampton-engq3-gb	europe/london	52.58547	-2.12296	252791
weston super mare-engj4-gb	europe/london	51.34603	-2.97665	139365
northampton-engj1-gb	europe/london	52.25	-0.88333	398985
york-engq5-gb	europe/london	53.95763	-1.08271	144202
mansfield-engj9-gb	europe/london	53.13333	-1.2	382471
nottingham-engj8-gb	europe/london	52.9536	-1.15047	246654
kirkcaldy-sctv1-gb	europe/london	56.10982	-3.16149	156104
halifax-engc2-gb	europe/london	53.71667	-1.85	115496
cambridge-engc3-gb	europe/london	52.2	0.11667	183259
paisley-sctw2-gb	europe/london	55.83173	-4.43254	124110
saint austell-engc6-gb	europe/london	50.33833	-4.76583	110196
coventry-engc7-gb	europe/london	52.40656	-1.51217	308313
oldham-engk1-gb	europe/london	53.54051	-2.1183	127630
oxford-engk2-gb	europe/london	51.75222	-1.25596	373721
peterborough-engk3-gb	europe/london	52.57364	-0.24777	140141
plymouth-engk4-gb	europe/london	50.37153	-4.14305	271400
poole-engk5-gb	europe/london	50.71667	-2.0	150092
portsmouth-engk6-gb	europe/london	50.79899	-1.09125	212664
reading-engk7-gb	europe/london	51.45625	-0.97113	244070
cardiff-wlsx5-gb	europe/london	51.48	-3.18	302139
dunstable-engz6-gb	europe/london	51.886	-0.52099	101166
bedford-engz5-gb	europe/london	52.13459	-0.46632	126531
coity-wlsx3-gb	europe/london	51.522	-3.55531	114423
chester-engz8-gb	europe/london	53.1905	-2.89189	217733
aberdeen-sctt5-gb	europe/london	57.14369	-2.09814	183790
sutton coldfield-eng00-gb	europe/london	52.56667	-1.81667	188393
bootle-eng00-gb	europe/london	53.46667	-3.01667	443183
dewsbury-eng00-gb	europe/london	53.69076	-1.62907	484994
durham-engd8-gb	europe/london	54.77676	-1.57566	278407
exeter-engd4-gb	europe/london	50.7236	-3.52751	226176
dudley-engd7-gb	europe/london	52.5	-2.08333	358608
weymouth-engd6-gb	europe/london	50.61136	-2.45334	127178
high peak-engd3-gb	europe/london	53.36797	-1.84536	330557
long eaton-engd3-gb	europe/london	52.89855	-1.27136	150567
derby-engd2-gb	europe/london	52.92277	-1.47663	235029
newport-wlsy6-gb	europe/london	51.58774	-2.99835	117326
west bromwich-engl7-gb	europe/london	52.51868	-1.9945	206955
shrewsbury-engl6-gb	europe/london	52.71009	-2.75208	102643
rotherham-engl3-gb	europe/london	53.43012	-1.35678	171775
sheffield-engl9-gb	europe/london	53.38297	-1.4659	447047
southport-engl8-gb	europe/london	53.64779	-3.00648	193622
rhondda-wlsy9-gb	europe/london	51.65896	-3.44885	122626
dundee-sctu3-gb	europe/london	56.5	-2.96667	151592
edinburgh-sctu8-gb	europe/london	55.95206	-3.19648	435791
birkenhead-engq1-gb	europe/london	53.39337	-3.01479	188334
worcester-engq4-gb	europe/london	52.18935	-2.22001	366682
runcorn-enge9-gb	europe/london	53.34174	-2.73124	115776
gloucester-enge6-gb	europe/london	51.86568	-2.2431	278784
colchester-enge4-gb	europe/london	51.88921	0.90421	703094
harlow-enge4-gb	europe/london	51.77655	0.11158	178109
gateshead-enge5-gb	europe/london	54.96209	-1.60168	128629
brighton-enge2-gb	europe/london	50.82838	-0.13947	407255
kingswood-engm6-gb	europe/london	51.45278	-2.50833	159117
south shields-engm7-gb	europe/london	54.99859	-1.4323	129727
swansea-wlsz1-gb	europe/london	51.62079	-3.94323	209668
southend on sea-engm5-gb	europe/london	51.53782	0.71433	163377
solihull-engm2-gb	europe/london	52.41426	-1.78094	128267
mendip-engm3-gb	europe/london	51.2372	-2.6266	295535
slough-engm1-gb	europe/london	51.50949	-0.59541	134072
newcastle under lyme-engm9-gb	europe/london	53.0	-2.23333	416350
belfast-nirr3-gb	europe/london	54.58333	-5.93333	274770
watford-engf8-gb	europe/london	51.65531	-0.39602	852470
basingstoke-engf2-gb	europe/london	51.26249	-1.08708	747413
gosport-engf2-gb	europe/london	50.79509	-1.12902	111433
stockton on tees-engn3-gb	europe/london	54.56848	-1.3187	115665
stockport-engn2-gb	europe/london	53.40979	-2.15761	183444
saint helens-engn1-gb	europe/london	53.45	-2.73333	119888
woking-engn7-gb	europe/london	51.31903	-0.55893	857000
sunderland-engn6-gb	europe/london	54.90465	-1.38222	177965
ipswich-engn5-gb	europe/london	52.05917	1.15545	249632
stoke on trent-engn4-gb	europe/london	53.00415	-2.18538	260419
swindon-engn9-gb	europe/london	51.55797	-1.78116	155432
gillingham-engg5-gb	europe/london	51.38914	0.54863	845600
margate-engg5-gb	europe/london	51.38132	1.38617	225437
hull-engg6-gb	europe/london	53.7446	-0.33525	302296
huddersfield-engg8-gb	europe/london	53.64904	-1.78416	195210
walsall-engo8-gb	europe/london	52.58528	-1.98396	228149
torquay-engo4-gb	europe/london	50.46384	-3.51434	133120
sale-engo6-gb	europe/london	53.42519	-2.32443	180388
wakefield-engo7-gb	europe/london	53.68331	-1.49768	145311
telford-engo2-gb	europe/london	52.67659	-2.44926	161057
salford-engl5-gb	europe/london	53.48771	-2.29042	148129
southampton-engm4-gb	europe/london	50.90395	-1.40428	246201
liverpool-engh8-gb	europe/london	53.41058	-2.97794	468945
east kilbride-sctw5-gb	europe/london	55.76667	-4.16667	163585
crewe-engz7-gb	europe/london	53.09787	-2.44161	202864
leeds-engh3-gb	europe/london	53.79648	-1.54785	571064
preston-engh2-gb	europe/london	53.76667	-2.71667	866524
loughborough-engh5-gb	europe/london	52.76667	-1.2	241619
leicester-engh4-gb	europe/london	52.6386	-1.13169	339239
lincoln-engh7-gb	europe/london	53.22683	-0.53792	212871
birmingham-enga7-gb	europe/london	52.48142	-1.89983	1009806
bath-enga4-gb	europe/london	51.37795	-2.35907	109117
blackburn-enga8-gb	europe/london	53.75	-2.48333	138720
blackpool-enga9-gb	europe/london	53.81667	-3.05	143101
nuneaton-engp3-gb	europe/london	52.52323	-1.46523	300914
warrington-engp2-gb	europe/london	53.39254	-2.58024	125031
wigan-engp7-gb	europe/london	53.53333	-2.61667	160890
crawley-engp6-gb	europe/london	51.11303	-0.18312	440798
salisbury-engp8-gb	europe/london	51.06931	-1.79569	152639
norwich-engi9-gb	europe/london	52.62783	1.29834	297000
manchester-engi2-gb	europe/london	53.48095	-2.23743	490681
luton-engi1-gb	europe/london	51.87967	-0.41748	193669
milton keynes-engi6-gb	europe/london	52.04172	-0.75583	199573
newcastle upon tyne-engi7-gb	europe/london	54.97328	-1.61396	233729
middlesbrough-engi5-gb	europe/london	54.57623	-1.23483	142707
libreville-01-ga	africa/libreville	0.39241	9.45356	578156
port gentil-08-ga	africa/libreville	-0.71933	8.78151	109163
kindia-d16-gn	africa/conakry	10.05692	-12.86576	117062
camayenne-04-gn	africa/conakry	9.535	-13.68778	3638442
kankan-k32-gn	africa/conakry	10.38542	-9.30568	114009
nzerekore-n38-gn	africa/conakry	7.75624	-8.8179	132728
kumasi-02-gh	africa/accra	6.68848	-1.62443	1468609
takoradi-00-gh	africa/accra	4.88447	-1.75536	253865
achiaman-00-gh	africa/accra	5.7	-0.33333	980429
obuasi-00-gh	africa/accra	6.20602	-1.66191	163266
techiman-00-gh	africa/accra	7.58616	-1.94137	101131
tafo-00-gh	africa/accra	6.73453	-1.61275	118474
nkawkaw-00-gh	africa/accra	6.55121	-0.7662	102475
accra-01-gh	africa/accra	5.55602	-0.1969	1963264
tamale-06-gh	africa/accra	9.40078	-0.8393	389889
cape coast-04-gh	africa/accra	5.10535	-1.2466	143015
sekondi takoradi-09-gh	africa/accra	4.934	-1.7137	138872
sumbawanga-24-tz	africa/dar_es_salaam	-7.96667	31.61667	113231
zanzibar-25-tz	africa/dar_es_salaam	-6.16394	39.19793	403658
arusha-26-tz	africa/dar_es_salaam	-3.36667	36.68333	409862
babati-27-tz	africa/dar_es_salaam	-4.21667	35.75	155372
moshi-06-tz	africa/dar_es_salaam	-3.35	37.33333	156959
iringa-04-tz	africa/dar_es_salaam	-7.76667	35.7	141013
dar es salaam-23-tz	africa/dar_es_salaam	-6.82349	39.26951	2717738
musoma-08-tz	africa/dar_es_salaam	-1.5	33.8	137495
mbeya-09-tz	africa/dar_es_salaam	-8.9	33.45	474842
bagamoyo-02-tz	africa/dar_es_salaam	-6.43333	38.9	166795
dodoma-03-tz	africa/dar_es_salaam	-6.17221	35.73947	180541
morogoro-10-tz	africa/dar_es_salaam	-6.82102	37.66122	250902
kilosa-10-tz	africa/dar_es_salaam	-6.83333	36.98333	109750
mwanza-12-tz	africa/dar_es_salaam	-2.51667	32.9	487845
shinyanga-15-tz	africa/dar_es_salaam	-3.66393	33.42118	216476
ushirombo-15-tz	africa/dar_es_salaam	-3.49194	31.96389	129832
somanda-15-tz	africa/dar_es_salaam	-3.36667	33.95	110935
songea-14-tz	africa/dar_es_salaam	-10.68333	35.65	145921
tabora-17-tz	africa/dar_es_salaam	-5.01622	32.82663	193512
singida-16-tz	africa/dar_es_salaam	-4.81629	34.74358	208465
bukoba-19-tz	africa/dar_es_salaam	-1.33167	31.81222	104759
buseresere-19-tz	africa/dar_es_salaam	-3.02361	31.87472	130337
tanga-18-tz	africa/dar_es_salaam	-5.06893	39.09875	257452
kigoma-05-tz	africa/dar_es_salaam	-4.87694	29.62667	181090
vientiane-24-la	asia/vientiane	17.96667	102.6	196731
kaohsiung-02-tw	asia/taipei	22.61626	120.31333	1519711
banqiao-03tpq-tw	asia/taipei	25.01427	121.46719	543342
hsinchu-04hsz-tw	asia/taipei	24.80361	120.96861	404109
taoyuan city-04-tw	asia/taipei	24.99368	121.29696	486563
buli-04-tw	asia/taipei	23.96639	120.96952	131554
hualian-04hua-tw	asia/taipei	23.97694	121.60444	350468
keelung-04kee-tw	asia/taipei	25.12825	121.7419	397515
douliu-04yun-tw	asia/taipei	23.70944	120.54333	104723
taichung-04txg-tw	asia/taipei	24.1469	120.6839	1040725
taipei-03tpe-tw	asia/taipei	25.04776	121.53185	7871900
tainan-04tnn-tw	asia/taipei	22.99083	120.21333	771235
nantou-04nan-tw	asia/taipei	23.91566	120.66387	105682
taitung city--tw	asia/taipei	22.7583	121.1444	110941
mon repos-10-tt	america/port_of_spain	10.283	-61.44605	138499
ordu-52-tr	europe/istanbul	40.98472	37.87889	234452
unieh-52-tr	europe/istanbul	41.13139	37.2825	109759
aydin-09-tr	europe/istanbul	37.84501	27.83963	390521
fethiye-48-tr	europe/istanbul	36.62167	29.11639	115470
mugla-48-tr	europe/istanbul	37.21807	28.3665	100934
tokat-60-tr	europe/istanbul	40.31389	36.55444	342636
trabzon-61-tr	europe/istanbul	41.005	39.72694	481728
sanliurfa-63-tr	europe/istanbul	37.16708	38.79392	534735
siverek-63-tr	europe/istanbul	37.75502	39.31667	175341
viransehir-63-tr	europe/istanbul	37.23528	39.76306	154163
usak-64-tr	europe/istanbul	38.67351	29.4058	169942
van-65-tr	europe/istanbul	38.49239	43.38311	371713
yozgat-66-tr	europe/istanbul	39.82	34.80444	186037
ankara-68-tr	europe/istanbul	39.91987	32.85427	4721256
gaziantep-83-tr	europe/istanbul	37.05944	37.3825	1148283
cizre-80-tr	europe/istanbul	37.32722	42.19028	231493
adana-81-tr	europe/istanbul	37.00167	35.32889	1377207
kozan-81-tr	europe/istanbul	37.45517	35.81573	158363
rize-53-tr	europe/istanbul	41.02083	40.52194	185293
kars-84-tr	europe/istanbul	40.60199	43.09495	102643
zonguldak-85-tr	europe/istanbul	41.45139	31.79305	256299
adiyaman-02-tr	europe/istanbul	37.76441	38.27629	338741
erzurum-25-tr	europe/istanbul	39.90861	41.27694	460706
eskisehir-26-tr	europe/istanbul	39.77667	30.52056	514869
denizli-20-tr	europe/istanbul	37.77417	29.0875	349344
antalya-07-tr	europe/istanbul	36.90812	30.69556	926138
alanya-07-tr	europe/istanbul	36.54375	31.99982	131340
edirne-22-tr	europe/istanbul	41.67719	26.55597	162940
elazig-23-tr	europe/istanbul	38.67431	39.22321	313926
kahramanmaras-46-tr	europe/istanbul	37.5847	36.9264	415425
elbistan-46-tr	europe/istanbul	38.20591	37.1983	120069
malatya-44-tr	europe/istanbul	38.35018	38.31667	441805
manisa-45-tr	europe/istanbul	38.61202	27.42646	431922
salihli-45-tr	europe/istanbul	38.48258	28.14774	160741
giresun-28-tr	europe/istanbul	40.91698	38.38741	167909
kutahya-43-tr	europe/istanbul	39.42417	29.98333	237190
kirsehir-40-tr	europe/istanbul	39.14583	34.16389	139463
gebze-41-tr	europe/istanbul	40.80276	29.43068	655301
karaman-78-tr	europe/istanbul	37.18111	33.215	120399
erzincan-24-tr	europe/istanbul	39.75222	39.49278	153618
afyonkarahisar-03-tr	europe/istanbul	38.75667	30.54333	279202
tatvan-13-tr	europe/istanbul	38.50667	42.28167	179045
batman-76-tr	europe/istanbul	37.88738	41.13221	331576
aksaray-75-tr	europe/istanbul	38.37255	34.02537	183345
siirt-74-tr	europe/istanbul	37.93262	41.94025	146148
nigde-73-tr	europe/istanbul	37.96583	34.67935	123474
kiziltepe-72-tr	europe/istanbul	37.19319	40.58799	253619
nusaybin-72-tr	europe/istanbul	37.0778	41.2178	165245
konya-71-tr	europe/istanbul	37.87135	32.48464	936488
eregli-71-tr	europe/istanbul	37.51333	34.04672	141626
hakkari-70-tr	europe/istanbul	37.57444	43.74083	149428
osmaniye-91-tr	europe/istanbul	37.07417	36.24778	202837
kirikkale-79-tr	europe/istanbul	39.84528	33.50639	260817
diyarbakir-21-tr	europe/istanbul	37.91583	40.21889	719256
silvan-21-tr	europe/istanbul	38.14194	41.00806	108861
balikesir-10-tr	europe/istanbul	39.64917	27.88611	278209
bandirma-10-tr	europe/istanbul	40.35222	27.97667	171072
edremit-10-tr	europe/istanbul	39.59611	27.02444	114053
luleburgaz-39-tr	europe/istanbul	41.40385	27.35918	175846
kayseri-38-tr	europe/istanbul	38.73222	35.48528	686765
corlu-59-tr	europe/istanbul	41.15917	27.8	391943
sivas-58-tr	europe/istanbul	39.74833	37.01611	264022
canakkale-17-tr	europe/istanbul	40.14556	26.40639	128646
bursa-16-tr	europe/istanbul	40.19167	29.06111	1753371
samsun-55-tr	europe/istanbul	41.28667	36.33	554679
mercin-32-tr	europe/istanbul	36.79526	34.61792	840894
iskenderun-31-tr	europe/istanbul	36.58718	36.17347	553116
amasya-05-tr	europe/istanbul	40.65333	35.83306	200379
kastamonu-37-tr	europe/istanbul	41.37805	33.77528	111906
agri-04-tr	europe/istanbul	39.71944	43.05139	110791
izmir-35-tr	europe/istanbul	38.41273	27.13838	3256488
hypaepa-35-tr	europe/istanbul	38.2278	27.96955	114373
istanbul-34-tr	europe/istanbul	41.01384	28.94966	17484590
silivri-34-tr	europe/istanbul	41.08022	28.22605	103669
corum-19-tr	europe/istanbul	40.54889	34.95333	266709
karabuk-89-tr	europe/istanbul	41.20488	32.62768	132723
adapazari-54-tr	europe/istanbul	40.78056	30.40333	470859
mus-49-tr	europe/istanbul	38.74525	41.50693	101227
bingol-12-tr	europe/istanbul	38.88472	40.49389	118364
isparta-33-tr	europe/istanbul	37.76444	30.55222	205481
point pedro-38-lk	asia/colombo	9.81667	80.23333	168015
jaffna-31-lk	asia/colombo	9.66845	80.00742	169102
trincomalee-37-lk	asia/colombo	8.5711	81.2335	108420
kalmunai-37-lk	asia/colombo	7.41667	81.81667	228243
colombo-36-lk	asia/colombo	6.93194	79.84778	2186755
galle-34-lk	asia/colombo	6.0367	80.217	248684
kandy-29-lk	asia/colombo	7.2955	80.6356	177279
riga-25-lv	europe/riga	56.946	24.10589	742572
daugavpils-06-lv	europe/riga	55.88333	26.53333	111564
vec liepaja-16-lv	europe/riga	56.53333	21.01667	170392
klaipeda-58-lt	europe/vilnius	55.71722	21.1175	210103
kaunas-57-lt	europe/vilnius	54.9	23.9	374643
panevezys-60-lt	europe/vilnius	55.73333	24.35	117395
siauliai-61-lt	europe/vilnius	55.93333	23.31667	130587
vilnius-65-lt	europe/vilnius	54.68916	25.2798	542366
balkanabat-02-tm	asia/ashgabat	39.51075	54.36713	112134
dasoguz-03-tm	asia/ashgabat	41.83625	59.96662	166500
ashgabat-01-tm	asia/ashgabat	37.95	58.38333	767181
turkmenabat-04-tm	asia/ashgabat	39.07328	63.57862	252579
mary-05-tm	asia/ashgabat	37.59378	61.83031	190477
monrovia-14-lr	africa/monrovia	6.30054	-10.7969	972712
maseru-14-ls	africa/maseru	-29.31667	27.48333	118355
kanchanaburi-50-th	asia/bangkok	14.00412	99.54832	160138
surat thani-60-th	asia/bangkok	9.14011	99.33311	174911
phuket-62-th	asia/bangkok	7.89059	98.3981	289787
nakhon si thammarat-64-th	asia/bangkok	8.43333	99.96667	200694
hat yai-68-th	asia/bangkok	7.00836	100.47668	409095
chiang mai-02-th	asia/bangkok	18.79038	98.98468	269606
chiang rai-03-th	asia/bangkok	19.90858	99.8325	116428
nakhon ratchasima-27-th	asia/bangkok	14.97066	102.10196	294778
lampang-06-th	asia/bangkok	18.29232	99.49277	156139
chanthaburi-48-th	asia/bangkok	12.60961	102.10447	138330
chon buri-46-th	asia/bangkok	13.3622	100.98345	601741
rayong-47-th	asia/bangkok	12.68095	101.25798	190560
samut prakan-42-th	asia/bangkok	13.59934	100.59675	619782
bangkok-40-th	asia/bangkok	13.75398	100.50144	5104476
phetchabun-14-th	asia/bangkok	16.41904	101.16056	113288
udon thani-76-th	asia/bangkok	17.41567	102.78589	322860
ubon ratchathani-75-th	asia/bangkok	15.23844	104.84866	221187
phitsanulok-12-th	asia/bangkok	16.82481	100.25858	139142
ban rangsit-39-th	asia/bangkok	14.02775	100.75603	327180
mueang nonthaburi-38-th	asia/bangkok	13.86075	100.51477	594353
khon kaen-22-th	asia/bangkok	16.44671	102.833	183162
nong khai-17-th	asia/bangkok	17.87847	102.742	114109
nakhon sawan-16-th	asia/bangkok	15.70472	100.13717	109308
krathum baen-55-th	asia/bangkok	13.6533	100.25972	178221
hua hin-57-th	asia/bangkok	12.57065	99.95876	117458
cha am-56-th	asia/bangkok	12.8	99.96667	138578
saraburi-37-th	asia/bangkok	14.53333	100.91667	212129
phra nakhon si ayutthaya-36-th	asia/bangkok	14.35167	100.57739	216320
nakhon pathom-53-th	asia/bangkok	13.8196	100.04427	172956
ratchaburi-52-th	asia/bangkok	13.53671	99.81712	254242
narathiwat-31-th	asia/bangkok	6.42639	101.82308	124650
lome-24-tg	africa/lome	6.13748	1.21227	873623
sokode-22-tg	africa/lome	8.98333	1.13333	164533
kara-23-tg	africa/lome	9.55111	1.18611	150011
n'djamena-15-td	africa/ndjamena	12.10672	15.0444	721081
sagh-17-td	africa/ndjamena	9.1429	18.3923	102528
moundou-08-td	africa/ndjamena	8.56667	16.08333	135167
tagiura-61-ly	africa/tripoli	32.88167	13.35056	100000
yafran-62-ly	africa/tripoli	32.06329	12.52859	100638
al bayda'-63-ly	africa/tripoli	32.76272	21.75506	206180
benghazi-69-ly	africa/tripoli	32.11667	20.06667	650629
zawiya-68-ly	africa/tripoli	32.75222	12.72778	288161
ajdabiya-83-ly	africa/tripoli	30.75545	20.22626	134358
tarhuna-82-ly	africa/tripoli	32.43502	13.6332	210697
al khums-82-ly	africa/tripoli	32.64861	14.26191	201943
zlitan-45-ly	africa/tripoli	32.46738	14.56874	109972
tripoli-77-ly	africa/tripoli	32.87519	13.18746	1150989
surt-76-ly	africa/tripoli	31.20892	16.58866	128123
sabha-75-ly	africa/tripoli	27.03766	14.42832	130000
misratah-72-ly	africa/tripoli	32.37535	15.09254	386120
tobruk-79-ly	africa/tripoli	32.08361	23.97639	121052
al jadid-34-ly	africa/tripoli	27.05	14.4	126386
san pedro de macoris-24-do	america/santo_domingo	18.46156	-69.29718	235593
santiago de los caballeros-25-do	america/santo_domingo	19.45	-70.7	1256441
san francisco de macoris-06-do	america/santo_domingo	19.29518	-70.25543	124763
punta cana-23-do	america/santo_domingo	18.58182	-68.40431	100023
salvaleon de higuey-10-do	america/santo_domingo	18.61501	-68.70798	123787
la romana-12-do	america/santo_domingo	18.42734	-68.97285	208437
san cristobal-33-do	america/santo_domingo	18.41667	-70.1	260851
puerto plata-18-do	america/santo_domingo	19.79344	-70.6884	146000
concepcion de la vega-30-do	america/santo_domingo	19.22207	-70.52956	161890
santo domingo-34-do	america/santo_domingo	18.50012	-69.98857	2201941
djibouti-07-dj	africa/djibouti	11.58901	43.14503	623891
copenhagen-17101-dk	europe/copenhagen	55.67594	12.56553	1153615
aalborg-19851-dk	europe/copenhagen	57.048	9.9187	122219
odense-21461-dk	europe/copenhagen	55.39594	10.38831	145931
arhus-18751-dk	europe/copenhagen	56.15674	10.21076	237551
essen-07-de	europe/berlin	51.45657	7.01228	7965655
bonn-07-de	europe/berlin	50.73438	7.09548	2122071
siegen-07-de	europe/berlin	50.87482	8.02431	503801
gutersloh-07-de	europe/berlin	51.90693	8.37854	968276
minden-07-de	europe/berlin	52.28953	8.91455	188851
rheine-07-de	europe/berlin	52.28509	7.44055	360659
bocholt-07-de	europe/berlin	51.83879	6.61531	259030
stolberg-07-de	europe/berlin	50.77368	6.22595	460391
menden-07-de	europe/berlin	51.44337	7.77824	209282
rostock-1200-de	europe/berlin	54.0887	12.14049	198293
nuremberg-02-de	europe/berlin	49.44778	11.06833	946065
ingolstadt-02-de	europe/berlin	48.76508	11.42372	241828
bogenhausen-02-de	europe/berlin	48.15221	11.61585	324962
bamberg-02-de	europe/berlin	49.89873	10.90067	118948
schweinfurt-02-de	europe/berlin	50.04937	10.22175	144190
neu ulm-02-de	europe/berlin	48.39279	10.01112	153270
amberg-02-de	europe/berlin	49.44287	11.86267	115522
straubing-02-de	europe/berlin	48.88126	12.57385	111780
kaufbeuren-02-de	europe/berlin	47.88238	10.62192	126471
waldkraiburg-02-de	europe/berlin	48.20854	12.39893	100227
bremerhaven-03-de	europe/berlin	53.55021	8.57674	136309
mannheim-01-de	europe/berlin	49.49671	8.47955	704463
heilbronn-01-de	europe/berlin	49.13995	9.22054	1115878
ulm-01-de	europe/berlin	48.39841	9.99155	356344
reutlingen-01-de	europe/berlin	48.49144	9.20427	438447
villingen schwenningen-01-de	europe/berlin	48.06226	8.49358	283744
konstanz-01-de	europe/berlin	47.66033	9.17582	287357
offenburg-01-de	europe/berlin	48.47377	7.94495	297944
rheinfelden (baden)-01-de	europe/berlin	47.56013	7.78715	100395
braunschweig-06-de	europe/berlin	52.26594	10.52673	847099
osnabruck-06-de	europe/berlin	52.27264	8.0498	334868
oldenburg-06-de	europe/berlin	53.14118	8.21467	516803
gottingen-06-de	europe/berlin	51.53933	9.93406	258341
luneburg-06-de	europe/berlin	53.2509	10.41409	235212
garbsen-06-de	europe/berlin	52.41371	9.5899	536777
nordhorn-06-de	europe/berlin	52.43081	7.06833	176364
emden-06-de	europe/berlin	53.36745	7.20778	222014
stade-06-de	europe/berlin	53.59337	9.47629	103094
chemnitz-13145-de	europe/berlin	50.83333	12.91667	268558
hamburg-04-de	europe/berlin	53.57532	10.01534	4074850
leipzig-13147-de	europe/berlin	51.33962	12.37129	522580
mainz-08-de	europe/berlin	49.98419	8.2791	376803
ludwigshafen am rhein-08-de	europe/berlin	49.48121	8.44641	531456
koblenz-08-de	europe/berlin	50.35357	7.57884	337579
saarbrucken-09-de	europe/berlin	49.2354	6.98165	586816
kassel-05066-de	europe/berlin	51.31667	9.5	272496
karlsruhe-01082-de	europe/berlin	49.00472	8.38583	319366
freiburg-01083-de	europe/berlin	47.9959	7.85222	363377
stuttgart-01081-de	europe/berlin	48.78232	9.17702	1086726
bremen-0300-de	europe/berlin	53.07516	8.80777	546501
wuerzburg-02096-de	europe/berlin	49.78778	9.93611	133731
augsburg-02097-de	europe/berlin	48.36667	10.88333	309427
muenchen-02091-de	europe/berlin	48.13743	11.57549	1654349
regensburg-02093-de	europe/berlin	49.015	12.09556	129151
hamm-07059-de	europe/berlin	51.68033	7.82089	331302
blieskastel-0900-de	europe/berlin	49.23724	7.25617	215638
koeln-07053-de	europe/berlin	50.93333	6.95	1493829
aachen-07053-de	europe/berlin	50.77664	6.08342	353779
dusseldorf-07051-de	europe/berlin	51.22172	6.77616	979135
bielefeld-07057-de	europe/berlin	52.03333	8.53333	889775
muenster-07055-de	europe/berlin	51.96236	7.62571	431812
halle neustadt-14-de	europe/berlin	51.47924	11.91605	818938
magdeburg-14-de	europe/berlin	52.12773	11.62916	609539
potsdam-11-de	europe/berlin	52.39886	13.06566	487869
cottbus-11-de	europe/berlin	51.75769	14.32888	213566
eberswalde-11-de	europe/berlin	52.83492	13.81951	139717
kiel-10-de	europe/berlin	54.32133	10.13489	435765
norderstedt-10-de	europe/berlin	53.6859	9.98041	445585
zwickau-13-de	europe/berlin	50.72724	12.48839	406174
gorlitz-13-de	europe/berlin	51.15518	14.98853	165981
freiberg-13-de	europe/berlin	50.91089	13.33881	203222
delitzsch-13-de	europe/berlin	51.52546	12.34284	134527
schwerin-12-de	europe/berlin	53.62937	11.41316	161057
neubrandenburg-12-de	europe/berlin	53.56414	13.27532	111843
stralsund-12-de	europe/berlin	54.30911	13.0818	128859
erfurt-15-de	europe/berlin	50.9787	11.03283	692788
gera-15-de	europe/berlin	50.88029	12.08187	167374
dresden-13146-de	europe/berlin	51.05089	13.73832	576575
berlin-1600-de	europe/berlin	52.52437	13.41053	8660386
wiesbaden-05-de	europe/berlin	50.08258	8.24932	1374466
marburg an der lahn-05-de	europe/berlin	50.80904	8.77069	310031
bensheim-05-de	europe/berlin	49.68369	8.61839	237506
trier-0800-de	europe/berlin	49.75565	6.63935	100129
frankfurt am main-05064-de	europe/berlin	50.11552	8.68417	1104625
hannover-0600-de	europe/berlin	52.37052	9.73322	652265
delmenhorst-0600-de	europe/berlin	53.0511	8.63091	303145
luebeck-1000-de	europe/berlin	53.86893	10.68729	270773
aden-02-ye	asia/aden	12.77944	45.03667	550602
ta`izz-25-ye	asia/aden	13.57952	44.02091	615222
sanaa-26-ye	asia/aden	15.35472	44.20667	1937451
al mukalla-04-ye	asia/aden	14.54248	49.12424	258132
ibb-23-ye	asia/aden	13.96667	44.18333	305884
al hudaydah-08-ye	asia/aden	14.79781	42.95452	666089
sayyan-16-ye	asia/aden	15.17177	44.32442	101263
oued rhiou-51-dz	africa/algiers	35.96124	0.91896	193410
reguiba-43-dz	africa/algiers	33.56391	6.70326	129465
tolga-19-dz	africa/algiers	34.72224	5.37845	103231
'ain temouchent-36-dz	africa/algiers	35.29749	-1.14037	185454
batna-03-dz	africa/algiers	35.55597	6.17414	513168
algiers-01-dz	africa/algiers	36.7525	3.04197	2528129
medea-06-dz	africa/algiers	36.26417	2.75393	305446
mostaganem-07-dz	africa/algiers	35.93115	0.08918	130000
constantine-04-dz	africa/algiers	36.365	6.61472	681073
guelma-23-dz	africa/algiers	36.46214	7.42608	186751
oran-09-dz	africa/algiers	35.69111	-0.64167	946498
ain beida-29-dz	africa/algiers	35.79639	7.39278	269628
ain fakroun-29-dz	africa/algiers	35.97108	6.87374	100930
boumerdas-40-dz	africa/algiers	36.76639	3.47717	1154061
ech chettia-41-dz	africa/algiers	36.19591	1.25538	320224
sidi aissa-27-dz	africa/algiers	35.88548	3.77236	112267
boghni-14-dz	africa/algiers	36.54222	3.95306	400376
laghouat-25-dz	africa/algiers	33.8	2.86514	113872
sougueur-13-dz	africa/algiers	35.18568	1.49612	207390
el eulma-12-dz	africa/algiers	36.15281	5.69016	219778
beni mered-20-dz	africa/algiers	36.52389	2.86131	561140
lakhdaria-21-dz	africa/algiers	36.56463	3.5933	177647
saida-10-dz	africa/algiers	34.83034	0.15171	127497
el achir-39-dz	africa/algiers	36.06386	4.62744	316795
bechar-38-dz	africa/algiers	31.61667	-2.21667	143382
tlemcen-15-dz	africa/algiers	34.87833	-1.315	494385
ain oussera-22-dz	africa/algiers	35.45139	2.90583	169896
messaad-22-dz	africa/algiers	34.15429	3.50309	131401
baraki-55-dz	africa/algiers	36.66655	3.09606	376621
bejaia-18-dz	africa/algiers	36.75587	5.08433	321435
skikda-31-dz	africa/algiers	36.87617	6.90921	317345
sidi bel abbes-30-dz	africa/algiers	35.18994	-0.63085	239398
annaba-37-dz	africa/algiers	36.9	7.76667	327667
ouargla-50-dz	africa/algiers	31.94932	5.32502	210186
djamaa-50-dz	africa/algiers	33.53388	5.99306	204462
khemis miliana-35-dz	africa/algiers	36.26104	2.22015	176113
cheria-33-dz	africa/algiers	35.27306	7.75194	100631
chelghoum el aid-48-dz	africa/algiers	36.16286	6.16651	257591
berkane-54113-ma	africa/casablanca	34.92	-2.32	100332
sidi qacem-52-ma	africa/casablanca	34.22149	-5.70775	102557
ouazzane-52-ma	africa/casablanca	34.79711	-5.58224	102743
rabat-49421-ma	africa/casablanca	34.01325	-6.83255	1655753
sale-49-ma	africa/casablanca	34.03892	-6.8166	948335
safi-51431-ma	africa/casablanca	32.29939	-9.23718	288163
tangier-57511-ma	africa/casablanca	35.76727	-5.79975	688356
nador-54381-ma	africa/casablanca	35.16813	-2.93352	129260
kenitra-52281-ma	africa/casablanca	34.26101	-6.5802	366570
larache-57331-ma	africa/casablanca	35.19321	-6.15572	109294
casablanca-45141-ma	africa/casablanca	33.58831	-7.61138	3144909
meknes-48061-ma	africa/casablanca	33.89352	-5.54727	545705
khouribga-50311-ma	africa/casablanca	32.88108	-6.9063	267624
taza-58561-ma	africa/casablanca	34.21	-4.01	141890
marrakesh-47351-ma	africa/casablanca	31.63416	-7.99994	839296
settat-50461-ma	africa/casablanca	33.00103	-7.61662	213036
tetouan-57-ma	africa/casablanca	35.57845	-5.36837	362541
ksar el kebir-57-ma	africa/casablanca	35.00174	-5.90534	108753
el jadida-51181-ma	africa/casablanca	33.25492	-8.50602	184689
fes-46231-ma	africa/casablanca	34.03715	-4.9998	964891
khemisset-49291-ma	africa/casablanca	33.82404	-6.06627	177001
mohammedia-45371-ma	africa/casablanca	33.68607	-7.38298	187708
agadir-55001-ma	africa/casablanca	30.42018	-9.59815	698310
beni mellal-56091-ma	africa/casablanca	32.33725	-6.34984	207598
oujda-54411-ma	africa/casablanca	34.68052	-1.90764	405253
doha-01-qa	asia/qatar	25.27932	51.52245	344939
ar rayyan-06-qa	asia/qatar	25.29194	51.42444	272465
kabwe-02-zm	africa/lusaka	-14.4469	28.44644	188979
livingstone-07-zm	africa/lusaka	-17.84194	25.85425	109203
kitwe-08-zm	africa/lusaka	-12.80243	28.21323	1244436
lusaka-09-zm	africa/lusaka	-15.40669	28.28713	1314994
laayoune / el aaiun-00-eh	africa/el_aaiun	27.16224	-13.20315	188084
tallinn-01-ee	europe/tallinn	59.43696	24.75353	410654
tartu-18-ee	europe/tallinn	58.38062	26.72509	101092
kafr ad dawwar-03-eg	africa/cairo	31.13385	30.12843	792047
al mansurah-01-eg	africa/cairo	31.03637	31.38069	1033770
al matariyah-01-eg	africa/cairo	31.18287	32.03108	204796
alexandria-06-eg	africa/cairo	31.21564	29.95527	3811516
ismailia-07-eg	africa/cairo	30.60427	32.27225	336382
al fayyum-04-eg	africa/cairo	29.30995	30.8418	487154
qina-23-eg	africa/cairo	26.16418	32.72671	349740
al jizah-08-eg	africa/cairo	30.00808	31.21093	2728845
minuf-09-eg	africa/cairo	30.46579	30.93164	345057
luxor-28-eg	africa/cairo	25.69893	32.6421	422407
suhaj-24-eg	africa/cairo	26.55695	31.69478	685462
al `arish-27-eg	africa/cairo	31.13159	33.79844	128855
damietta-20-eg	africa/cairo	31.41648	31.81332	175133
kafr ash shaykh-21-eg	africa/cairo	31.1143	30.94012	403113
cairo-11-eg	africa/cairo	30.06263	31.24967	7964614
al minya-10-eg	africa/cairo	28.10988	30.7503	624669
banha-12-eg	africa/cairo	30.45906	31.17858	510731
suez-15-eg	africa/cairo	29.97371	32.52627	533677
az zaqaziq-14-eg	africa/cairo	30.58768	31.502	893131
asyut-17-eg	africa/cairo	27.18096	31.18368	751861
aswan-16-eg	africa/cairo	24.09343	32.90704	301048
idfu-16-eg	africa/cairo	24.98028	32.87472	166102
port said-19-eg	africa/cairo	31.25654	32.28412	538378
bani suwayf-18-eg	africa/cairo	29.07441	31.09785	377285
al mahallah al kubra-05-eg	africa/cairo	30.9745	31.16499	1136690
johannesburg-06jhb-za	africa/johannesburg	-26.20227	28.04363	4119525
pretoria-06tsh-za	africa/johannesburg	-25.74486	28.18783	1975731
east london-05buf-za	africa/johannesburg	-33.01529	27.91162	615963
noorder paarl-11dc2-za	africa/johannesburg	-33.70468	18.96552	451321
durban-02eth-za	africa/johannesburg	-29.8579	31.0292	3280813
george-11dc4-za	africa/johannesburg	-33.963	22.46173	251290
pietermaritzburg-02-za	africa/johannesburg	-29.61678	30.39278	838244
newcastle-02-za	africa/johannesburg	-27.75796	29.9318	404838
richards bay-02-za	africa/johannesburg	-28.78301	32.03768	330326
vryheid-02-za	africa/johannesburg	-27.76952	30.79165	194934
welkom-03-za	africa/johannesburg	-27.98644	26.70661	781271
kroonstad-03-za	africa/johannesburg	-27.65036	27.23488	103992
phuthaditjhaba-03-za	africa/johannesburg	-28.52423	28.81582	119366
bethlehem-03-za	africa/johannesburg	-28.23078	28.30707	100291
sasolburg-03-za	africa/johannesburg	-26.81358	27.81695	148335
bothaville-03-za	africa/johannesburg	-27.3887	26.61701	126889
vereeniging-06-za	africa/johannesburg	-26.67313	27.92615	942465
krugersdorp-06-za	africa/johannesburg	-26.08577	27.77515	694779
witbank-07-za	africa/johannesburg	-25.87133	29.23323	432252
embalenhle-07-za	africa/johannesburg	-26.53333	29.06667	384107
nelspruit-07-za	africa/johannesburg	-25.47448	30.97033	194040
piet retief-07-za	africa/johannesburg	-27.00706	30.81323	112476
queenstown-05-za	africa/johannesburg	-31.89756	26.87533	150359
grahamstown-05-za	africa/johannesburg	-33.30422	26.53276	109507
polokwane-09-za	africa/johannesburg	-23.90448	29.46885	157057
phalaborwa-09-za	africa/johannesburg	-23.94299	31.14107	109468
mokopane-09-za	africa/johannesburg	-24.19436	29.00974	101090
warmbaths-09-za	africa/johannesburg	-24.88333	28.28333	110737
bloemfontein-03man-za	africa/johannesburg	-29.12106	26.214	463064
botshabelo-03man-za	africa/johannesburg	-29.27016	26.7052	348330
port elizabeth-05nma-za	africa/johannesburg	-33.91799	25.57007	1196589
benoni-06eku-za	africa/johannesburg	-26.18848	28.32078	2194897
cape town-11cpt-za	africa/johannesburg	-33.92584	18.42322	3493707
kimberley-08dc9-za	africa/johannesburg	-28.73226	24.76232	142089
klerksdorp-10-za	africa/johannesburg	-26.85213	26.66672	541501
rustenburg-10-za	africa/johannesburg	-25.66756	27.24208	124064
brits-10-za	africa/johannesburg	-25.63473	27.78022	191264
cuenca-02-ec	america/guayaquil	-2.88333	-78.98333	294086
riobamba-06-ec	america/guayaquil	-1.66667	-78.63333	124478
machala-08-ec	america/guayaquil	-3.26667	-79.96667	324556
ibarra-11-ec	america/guayaquil	0.35	-78.11667	158452
guayaquil-10-ec	america/guayaquil	-2.16667	-79.9	2238366
la libertad-10-ec	america/guayaquil	-2.23333	-80.9	119743
quevedo-13-ec	america/guayaquil	-1.03333	-79.45	166144
babahoyo-13-ec	america/guayaquil	-1.81667	-79.51667	124323
loja-12-ec	america/guayaquil	-3.99313	-79.20422	136361
manta-14-ec	america/guayaquil	-0.95	-80.73333	423030
ambato-19-ec	america/guayaquil	-1.24908	-78.61675	170941
quito-18-ec	america/guayaquil	-0.22985	-78.52495	1425556
santo domingo de los colorados-18-ec	america/guayaquil	-0.25	-79.15	200421
kumanovo-d7-mk	europe/skopje	42.13222	21.71444	108471
skopje-41-mk	europe/skopje	42.00122	21.42878	474889
dire dawa-48-et	africa/addis_ababa	9.59306	41.86611	252279
bahir dar-46-et	africa/addis_ababa	11.59364	37.39077	218658
gonder-46-et	africa/addis_ababa	12.6	37.46667	153914
dese-46-et	africa/addis_ababa	11.13333	39.63333	248921
hawassa-54-et	africa/addis_ababa	7.06205	38.47635	169389
addis ababa-44-et	africa/addis_ababa	9.02497	38.74689	2757729
nazret-51-et	africa/addis_ababa	8.55	39.26667	369877
jima-51-et	africa/addis_ababa	7.66667	36.83333	156574
mekele-53-et	africa/addis_ababa	13.49667	39.47528	215546
gweru-02-zw	africa/harare	-19.45	29.81667	163148
harare-10-zw	africa/harare	-17.82772	31.05337	2006423
mutare-01-zw	africa/harare	-18.9707	32.67086	184205
kadoma-05-zw	africa/harare	-18.33328	29.91534	126468
bulawayo-09-zw	africa/harare	-20.15	28.58333	699385
badajoz-57ba-es	europe/madrid	38.87789	-6.97061	164570
merida-57ba-es	europe/madrid	38.91611	-6.34366	151612
sevilla-51se-es	europe/madrid	37.38241	-5.97613	1316512
tarragona-56t-es	europe/madrid	41.11667	1.25	427126
guadalajara-54gu-es	europe/madrid	40.63333	-3.16667	115783
lleida-56l-es	europe/madrid	41.61667	0.61667	169237
a coruna-58c-es	europe/madrid	43.37135	-8.396	503694
santiago de compostela-58c-es	europe/madrid	42.88052	-8.54569	186283
leon-55le-es	europe/madrid	42.6	-5.56667	182224
barcelona-56b-es	europe/madrid	41.38879	2.15899	6074192
vic-56b-es	europe/madrid	41.93012	2.25486	136504
bilbao-59bi-es	europe/madrid	43.26271	-2.92528	1039210
vitoria gasteiz-59vi-es	europe/madrid	42.85	-2.66667	253975
madrid-29m-es	europe/madrid	40.4165	-3.70256	9077356
vigo-58po-es	europe/madrid	42.23282	-8.72264	626504
logrono-27lo-es	europe/madrid	42.46667	-2.45	176894
almeria-51al-es	europe/madrid	36.83814	-2.45974	420106
granada-51gr-es	europe/madrid	37.18817	-3.60667	469986
ciudad real-54cr-es	europe/madrid	38.98333	-3.93333	163569
tomelloso-54cr-es	europe/madrid	39.15218	-3.02431	100287
ourense-58or-es	europe/madrid	42.33333	-7.85	107742
girona-56gi-es	europe/madrid	41.98311	2.82493	383464
valladolid-55va-es	europe/madrid	41.65518	-4.72372	361166
salamanca-55sa-es	europe/madrid	40.96667	-5.65	155619
valencia-60v-es	europe/madrid	39.46975	-0.37739	1816247
gandia-60v-es	europe/madrid	38.96667	-0.18333	175560
toledo-54to-es	europe/madrid	39.8581	-4.02263	119786
albacete-54ab-es	europe/madrid	38.98333	-1.85	185776
huelva-51h-es	europe/madrid	37.25833	-6.95083	293566
castello de la plana-60cs-es	europe/madrid	39.98333	-0.03333	334527
murcia-31mu-es	europe/madrid	37.98704	-1.13004	1065052
lorca-31mu-es	europe/madrid	37.67119	-1.7017	142674
cordoba-51co-es	europe/madrid	37.88333	-4.76667	394771
lucena-51co-es	europe/madrid	37.40881	-4.48522	117146
jaen-51j-es	europe/madrid	37.76667	-3.78333	335131
alicante-60a-es	europe/madrid	38.34517	-0.48149	1402056
denia-60a-es	europe/madrid	38.84078	0.10574	105723
las palmas de gran canaria-53gc-es	atlantic/canary	28.09973	-15.41343	774569
arrecife-53gc-es	atlantic/canary	28.96302	-13.54769	146911
jerez de la frontera-51ca-es	europe/madrid	36.68645	-6.13606	800934
algeciras-51ca-es	europe/madrid	36.13326	-5.45051	273069
malaga-51ma-es	europe/madrid	36.72016	-4.42034	1270836
estepona-51ma-es	europe/madrid	36.42764	-5.14589	102419
burgos-55bu-es	europe/madrid	42.35	-3.7	178966
palma-07pm-es	europe/madrid	39.56939	2.65024	627856
ibiza-07pm-es	europe/madrid	38.90883	1.43296	124021
pamplona-32na-es	europe/madrid	42.81687	-1.64323	325864
gijon-34o-es	europe/madrid	43.53573	-5.66152	742572
santa cruz de tenerife-53tf-es	atlantic/canary	28.46824	-16.25462	609557
arona-53tf-es	atlantic/canary	28.09962	-16.68102	198526
san sebastian-59ss-es	europe/madrid	43.31283	-1.97499	440526
lugo-58lu-es	europe/madrid	43.0	-7.56667	112115
santander-39s-es	europe/madrid	43.46472	-3.80444	335078
zaragoza-52z-es	europe/madrid	41.65606	-0.87734	878509
asmera-05-er	africa/asmara	15.33805	38.93184	563930
orel-56-ru	europe/moscow	52.96508	36.0785	371809
kostroma-37-ru	europe/moscow	57.76647	40.92686	320708
nal'chik-22-ru	europe/moscow	43.49806	43.61889	465083
yoshkar ola-45-ru	europe/moscow	56.63877	47.89078	295507
lipetsk-43-ru	europe/moscow	52.60311	39.57076	563068
yelets-43-ru	europe/moscow	52.62366	38.50169	115688
pskov-60-ru	europe/moscow	57.8136	28.3496	201990
velikiye luki-60-ru	europe/moscow	56.34	30.54517	103149
rostov na donu-61-ru	europe/moscow	47.23135	39.72328	1488152
taganrog-61-ru	europe/moscow	47.23617	38.89688	279056
shakhty-61-ru	europe/moscow	47.70911	40.21443	494863
volgodonsk-61-ru	europe/moscow	47.51361	42.15139	200750
kamensk shakhtinskiy-61-ru	europe/moscow	48.31779	40.25948	174185
yaroslavl'-88-ru	europe/moscow	57.62987	39.87368	669176
rybinsk-88-ru	europe/moscow	58.0446	38.84259	216724
yakutsk-63-ru	asia/yakutsk	62.03389	129.73306	235600
yuzhno sakhalinsk-64-ru	asia/sakhalin	46.95407	142.73603	211575
samara-65-ru	europe/samara	53.20006	50.15	1408107
tol'yatti-65-ru	europe/samara	53.5303	49.3461	702879
syzran'-65-ru	europe/samara	53.1585	48.4681	189338
saint petersburg-66-ru	europe/moscow	59.89444	30.26417	4589816
saratov-67-ru	europe/volgograd	51.54056	46.00861	1091585
balakovo-67-ru	europe/volgograd	52.02782	47.8007	270072
vladikavkaz-68-ru	europe/moscow	43.03667	44.66778	390952
smolensk-69-ru	europe/moscow	54.7818	32.0401	320991
izhevsk-80-ru	europe/samara	56.84976	53.20448	631038
glazov-80-ru	europe/samara	58.1393	52.658	117294
ul'yanovsk-81-ru	europe/moscow	54.32824	48.38657	657819
dimitrovgrad-81-ru	europe/moscow	54.21386	49.61838	132226
voronezh-86-ru	europe/moscow	51.67204	39.1843	951462
borisoglebsk-86-ru	europe/moscow	51.36713	42.08494	103821
noyabr'sk-87-ru	asia/yekaterinburg	63.19936	75.45067	110000
volgograd-84-ru	europe/volgograd	48.71939	44.50184	1369436
kamyshin-84-ru	europe/volgograd	50.09833	45.41601	144670
cherepovets-85-ru	europe/moscow	59.13333	37.9	333047
vologda-85-ru	europe/moscow	59.2187	39.8886	353196
elista-24-ru	europe/moscow	46.30778	44.25583	106971
kaluga-25-ru	europe/moscow	54.5293	36.27542	356129
obninsk-25-ru	europe/moscow	55.09681	36.61006	164293
maykop-01-ru	europe/moscow	44.60778	40.10583	173620
irkutsk-20-ru	asia/irkutsk	52.29778	104.29639	877312
bratsk-20-ru	asia/irkutsk	56.1325	101.61417	279100
ust' ilimsk-20-ru	asia/irkutsk	58.00056	102.66194	100271
astrakhan'-07-ru	europe/volgograd	46.34968	48.04076	518724
moscow-48-ru	europe/moscow	55.75222	37.61556	10900159
kaliningrad-23-ru	europe/kaliningrad	54.70649	20.51095	491613
saransk-46-ru	europe/moscow	54.1838	45.1749	352705
podol'sk-47-ru	europe/moscow	55.42418	37.55472	1586708
mytishchi-47-ru	europe/moscow	55.91163	37.73076	1475098
kolomna-47-ru	europe/moscow	55.07944	38.77833	511990
serpukhov-47-ru	europe/moscow	54.91578	37.41114	185559
orekhovo zuyevo-47-ru	europe/moscow	55.80672	38.96178	281117
klin-47-ru	europe/moscow	56.33333	36.73333	234666
naro fominsk-47-ru	europe/moscow	55.38752	36.73307	163352
ufa-08-ru	asia/yekaterinburg	54.78517	56.04562	1089576
sterlitamak-08-ru	asia/yekaterinburg	53.62462	55.95015	497545
neftekamsk-08-ru	asia/yekaterinburg	56.092	54.2661	173985
oktyabr'skiy-08-ru	asia/yekaterinburg	54.48147	53.47103	177029
meleuz-08-ru	asia/yekaterinburg	52.96667	55.91667	130683
gorod belgorod-09-ru	europe/moscow	50.59857	36.59273	1955692
staryy oskol-09-ru	europe/moscow	51.29667	37.84167	329238
petrozavodsk-28-ru	europe/moscow	61.78491	34.34691	299385
novokuznetsk-29-ru	asia/novokuznetsk	53.7557	87.1099	981520
kemerovo-29-ru	asia/novokuznetsk	55.33333	86.08333	580414
leninsk kuznetskiy-29-ru	asia/novokuznetsk	54.6567	86.1737	255029
mezhdurechensk-29-ru	asia/novokuznetsk	53.69417	88.06028	101026
anzhero sudzhensk-29-ru	asia/novokuznetsk	56.081	86.0285	106854
kurgan-40-ru	asia/yekaterinburg	55.45	65.33333	343129
kursk-41-ru	europe/moscow	51.73733	36.18735	456031
cherkessk-27-ru	europe/moscow	44.22333	42.05778	165343
velikiy novgorod-52-ru	europe/moscow	58.51667	31.28333	215062
blagoveshchensk-05-ru	asia/yakutsk	50.27817	127.54074	221296
arkhangel'sk-06-ru	europe/moscow	64.5401	40.5433	593243
kotlas-06-ru	europe/moscow	61.25745	46.64963	101807
nazran'-19-ru	europe/moscow	43.22597	44.77323	462275
vladimir-83-ru	europe/moscow	56.13655	40.39658	364999
kovrov-83-ru	europe/moscow	56.35722	41.31917	154224
murom-83-ru	europe/moscow	55.575	42.0426	142833
aleksandrov-83-ru	europe/moscow	56.39516	38.71216	234377
tver'-77-ru	europe/moscow	56.86049	35.87603	400212
vyshniy volochek-77-ru	europe/moscow	57.59125	34.56453	111315
tula-76-ru	europe/moscow	54.20213	37.64429	796036
donskoy-76-ru	europe/moscow	53.97106	38.33627	110700
tomsk-75-ru	asia/novosibirsk	56.4989	84.9762	595363
groznyy-12-ru	europe/moscow	43.31195	45.68895	400471
kazan-73-ru	europe/moscow	55.78874	49.12214	1221138
naberezhnyye chelny-73-ru	europe/moscow	55.72545	52.41122	856637
al'met'yevsk-73-ru	europe/moscow	54.90442	52.3154	248744
bugul'ma-73-ru	europe/moscow	54.5378	52.7985	114882
tambov-72-ru	europe/moscow	52.73169	41.44326	369967
yekaterinburg-71-ru	asia/yekaterinburg	56.8575	60.6125	1708519
nizhniy tagil-71-ru	asia/yekaterinburg	57.91944	59.965	534796
kamensk ural'skiy-71-ru	asia/yekaterinburg	56.4185	61.9329	214770
serov-71-ru	asia/yekaterinburg	59.60334	60.5787	191108
novoural'sk-71-ru	asia/yekaterinburg	57.24389	60.08389	116534
asbest-71-ru	asia/yekaterinburg	57.00993	61.45776	201501
stavropol'-70-ru	europe/moscow	45.0428	41.9734	600567
pyatigorsk-70-ru	europe/moscow	44.04861	43.05944	715133
budennovsk-70-ru	europe/moscow	44.78389	44.16583	109268
krasnoyarsk-91-ru	asia/krasnoyarsk	56.0091	92.8628	1082684
noril'sk-91-ru	asia/krasnoyarsk	69.3535	88.2027	227146
achinsk-91-ru	asia/krasnoyarsk	56.2694	90.4993	172886
kansk-91-ru	asia/krasnoyarsk	56.20167	95.7175	118170
perm'-90-ru	asia/yekaterinburg	58.01741	56.28552	1035108
berezniki-90-ru	asia/yekaterinburg	59.4091	56.8204	268560
lys'va-90-ru	asia/yekaterinburg	58.10861	57.80528	118865
chita-93-ru	asia/yakutsk	52.03171	113.50087	308500
petropavlovsk kamchatskiy-92-ru	asia/kamchatka	53.0465	158.65131	253178
kyzyl-79-ru	asia/krasnoyarsk	51.71472	94.45338	108240
tyumen'-78-ru	asia/yekaterinburg	57.15222	65.52722	534525
tobol'sk-78-ru	asia/yekaterinburg	58.19807	68.25457	113800
ulan ude-11-ru	asia/irkutsk	51.82721	107.60627	360278
bryansk-10-ru	europe/moscow	53.25209	34.37167	498360
klintsy-10-ru	europe/moscow	52.76019	32.23934	156474
chelyabinsk-13-ru	asia/yekaterinburg	55.15444	61.42972	1203594
magnitogorsk-13-ru	asia/yekaterinburg	53.41861	59.04722	413351
zlatoust-13-ru	asia/yekaterinburg	55.17111	59.65083	443698
ozersk-13-ru	asia/yekaterinburg	55.75556	60.70278	242867
troitsk-13-ru	asia/yekaterinburg	54.0979	61.5773	121538
trekhgornyy-13-ru	asia/yekaterinburg	54.815	58.45917	100647
krasnodar-38-ru	europe/moscow	45.0488	38.9725	879041
sochi-38-ru	europe/moscow	43.59917	39.72569	484808
novorossiysk-38-ru	europe/moscow	44.72439	37.76752	457862
armavir-38-ru	europe/moscow	44.9892	41.1234	345575
yeysk-38-ru	europe/moscow	46.7055	38.2739	106599
kropotkin-38-ru	europe/moscow	45.4375	40.57556	138998
slavyansk na kubani-38-ru	europe/moscow	45.2558	38.1256	111699
tikhoretsk-38-ru	europe/moscow	45.85472	40.12528	133608
belorechensk-38-ru	europe/moscow	44.76733	39.87424	116662
timashevsk-38-ru	europe/moscow	45.61694	38.94528	117914
kanevskaya-38-ru	europe/moscow	46.0849	38.9596	114507
vladivostok-59-ru	asia/vladivostok	43.10562	131.87353	771733
ussuriysk-59-ru	asia/vladivostok	43.80291	131.94578	157068
nakhodka-59-ru	asia/vladivostok	42.81384	132.87348	209409
barnaul-04-ru	asia/omsk	53.36056	83.76361	695385
biysk-04-ru	asia/omsk	52.53639	85.20722	215430
rubtsovsk-04-ru	asia/omsk	51.5	81.25	161065
makhachkala-17-ru	europe/moscow	42.97638	47.50236	642400
khasavyurt-17-ru	europe/moscow	43.2509	46.58766	160240
derbent-17-ru	europe/moscow	42.0678	48.28987	149878
cheboksary-16-ru	europe/moscow	56.13222	47.25194	575249
orenburg-55-ru	asia/yekaterinburg	51.7727	55.0988	550204
orsk-55-ru	asia/yekaterinburg	51.20487	58.56685	394641
omsk-54-ru	asia/omsk	55.0	73.4	1129281
penza-57-ru	europe/moscow	53.20066	45.00464	576181
kuznetsk-57-ru	europe/moscow	53.11675	46.60037	152619
khabarovsk-30-ru	asia/vladivostok	48.48272	135.08379	1157303
komsomol'sk na amure-30-ru	asia/vladivostok	50.55034	137.00995	322901
nizhniy novgorod-51-ru	europe/moscow	56.32867	44.00205	1800113
arzamas-51-ru	europe/moscow	55.39485	43.83992	109479
vyksa-51-ru	europe/moscow	55.3175	42.17444	116837
ryazan'-62-ru	europe/moscow	54.6269	39.6916	539332
novosibirsk-53-ru	asia/novosibirsk	55.0415	82.9346	1616835
iskitim-53-ru	asia/novosibirsk	54.6366	83.3045	103768
syktyvkar-34-ru	europe/moscow	61.67642	50.80994	286139
ukhta-34-ru	europe/moscow	63.56705	53.68348	131530
kirov-33-ru	europe/volgograd	58.59665	49.66007	579996
gatchina-42-ru	europe/moscow	59.57639	30.12833	168714
tikhvin-42-ru	europe/moscow	59.64511	33.52937	101513
vsevolozhsk-42-ru	europe/moscow	60.02043	30.63716	116524
ivanovo-21-ru	europe/moscow	56.99719	40.97139	630468
kineshma-21-ru	europe/moscow	57.43914	42.12894	132054
surgut-32-ru	asia/yekaterinburg	61.25	73.41667	441079
nizhnevartovsk-32-ru	asia/yekaterinburg	60.9344	76.5531	311628
murmansk-49-ru	europe/moscow	68.97917	33.09251	390516
apatity-49-ru	europe/moscow	67.56414	33.4031	155751
abakan-31-ru	asia/krasnoyarsk	53.71556	91.42917	238871
musanze-13-rw	africa/kigali	-1.49984	29.63497	157278
kigali-12-rw	africa/kigali	-1.94995	30.05885	745261
butare-15-rw	africa/kigali	-2.59667	29.73944	123432
gisenyi-14-rw	africa/kigali	-1.70278	29.25639	131647
krusevac-se19-rs	europe/belgrade	43.58	21.33389	124299
kragujevac-se12-rs	europe/belgrade	44.01667	20.91667	171782
cacak-se17-rs	europe/belgrade	43.89139	20.34972	141054
zemun-se0-rs	europe/belgrade	44.84306	20.40111	172412
novi sad-vo6-rs	europe/belgrade	45.25167	19.83694	296530
sremska mitrovica-vo7-rs	europe/belgrade	44.97639	19.61222	113777
subotica-vo1-rs	europe/belgrade	46.1	19.66667	116154
nis-se20-rs	europe/belgrade	43.32472	21.90333	250000
belgrade-se-rs	europe/belgrade	44.80401	20.46513	1273651
saint denis-re974-re	indian/reunion	-20.88231	55.4504	586433
saint pierre-re974-re	indian/reunion	-21.3393	55.47811	110349
arad-02-ro	europe/bucharest	46.18333	21.31667	169065
baia mare-25-ro	europe/bucharest	47.65729	23.56808	193952
drobeta turnu severin-26-ro	europe/bucharest	44.63194	22.65611	102346
targu mures-27-ro	europe/bucharest	46.54245	24.55747	164028
botosani-07-ro	europe/bucharest	47.75	26.66667	145559
bacau-04-ro	europe/bucharest	46.56667	26.9	237501
iasi-23-ro	europe/bucharest	47.16667	27.6	318012
braila-08-ro	europe/bucharest	45.26667	27.98333	213569
brasov-09-ro	europe/bucharest	45.64861	25.60613	321259
piatra neamt-28-ro	europe/bucharest	46.91667	26.33333	190980
slatina-29-ro	europe/bucharest	44.43333	24.36667	133375
focsani-40-ro	europe/bucharest	45.7	27.18333	105112
oradea-05-ro	europe/bucharest	47.06667	21.93333	224175
alba iulia-01-ro	europe/bucharest	46.06667	23.58333	182093
pitesti-03-ro	europe/bucharest	44.85	24.86667	199847
ramnicu valcea-39-ro	europe/bucharest	45.1	24.36667	107558
vaslui-38-ro	europe/bucharest	46.63333	27.73333	166172
hunedoara-21-ro	europe/bucharest	45.75	22.9	173689
buzau-11-ro	europe/bucharest	45.15	26.83333	169480
bucharest-10-ro	europe/bucharest	44.43225	26.10626	1877155
cluj napoca-13-ro	europe/bucharest	46.76667	23.6	459565
resita-12-ro	europe/bucharest	45.30083	21.88917	125098
constanta-14-ro	europe/bucharest	44.18333	28.65	419439
craiova-17-ro	europe/bucharest	44.31667	23.8	342736
targoviste-16-ro	europe/bucharest	44.92543	25.4567	124068
sibiu-33-ro	europe/bucharest	45.8	24.15	219976
galati-18-ro	europe/bucharest	45.45	28.05	294087
ploiesti-30-ro	europe/bucharest	44.95	26.01667	282201
timisoara-36-ro	europe/bucharest	45.75372	21.22571	315053
suceava-34-ro	europe/bucharest	47.63333	26.25	178341
targu jiu-19-ro	europe/bucharest	45.05	23.28333	119498
baia mare-32-ro	europe/bucharest	47.65331	23.57949	137976
satu mare-32-ro	europe/bucharest	47.8	22.88333	135073
nagarpur-00-bd	asia/dhaka	24.05	89.88333	770077
mymensingh-00-bd	asia/dhaka	24.75	90.4	283987
jamalpur-00-bd	asia/dhaka	24.91667	89.93333	249225
pabna-00-bd	asia/dhaka	24.0	89.25	219883
satkhira-00-bd	asia/dhaka	22.70817	89.07185	159844
faridpur-00-bd	asia/dhaka	23.6	89.83333	112187
bhairab bazar-00-bd	asia/dhaka	24.0524	90.9764	140017
bhola-00-bd	asia/dhaka	22.68759	90.64403	241858
palang-00-bd	asia/dhaka	23.21824	90.35076	142594
rajshahi-83-bd	asia/dhaka	24.36667	88.6	842494
bogra-83-bd	asia/dhaka	24.85	89.36667	475532
saidpur-83-bd	asia/dhaka	25.77769	88.89169	199422
khulna-82-bd	asia/dhaka	22.80978	89.56439	1495116
jessore-82-bd	asia/dhaka	23.16971	89.21371	331575
kushtia-82-bd	asia/dhaka	23.90105	89.12207	173883
dhaka-8113-bd	asia/dhaka	23.7104	90.40744	10356500
tungi-81-bd	asia/dhaka	23.89	90.40583	887824
sherpur-81-bd	asia/dhaka	25.01881	90.01751	107419
kishorganj-81-bd	asia/dhaka	24.43944	90.78291	169706
sylhet-86-bd	asia/dhaka	24.89904	91.87198	294441
rangpur-87-bd	asia/dhaka	25.75	89.25	481047
dinajpur-87-bd	asia/dhaka	25.62715	88.63864	311936
chittagong-84-bd	asia/dhaka	22.3384	91.83168	4167170
comilla-84-bd	asia/dhaka	23.46186	91.18504	516044
cox's bazar-84-bd	asia/dhaka	21.45388	91.96765	253788
feni-84-bd	asia/dhaka	23.01134	91.4013	148176
barisal-85-bd	asia/dhaka	22.70497	90.37013	332549
braine l'alleud-walwbr-be	europe/brussels	50.68363	4.36784	195679
gent-vlgvov-be	europe/brussels	51.05	3.71667	1035575
namur-walwna-be	europe/brussels	50.4669	4.86746	169516
leuven-vlgvbr-be	europe/brussels	50.87959	4.70093	601096
hasselt-vlgvli-be	europe/brussels	50.93106	5.33781	580608
charleroi-walwht-be	europe/brussels	50.41136	4.44448	706710
tournai-walwht-be	europe/brussels	50.60715	3.38932	180805
brussels-brubru-be	europe/brussels	50.85045	4.34878	1019022
liege-walwlg-be	europe/brussels	50.63373	5.56749	555073
brugge-vlgvwv-be	europe/brussels	51.20892	3.22424	746559
antwerpen-vlgvan-be	europe/brussels	51.21989	4.40346	1348465
bobo dioulasso-0951-bf	africa/ouagadougou	11.17715	-4.2979	360106
ouagadougou-0353-bf	africa/ouagadougou	12.36566	-1.53388	1086505
varna-61-bg	europe/sofia	43.21667	27.91667	312770
veliko turnovo-62-bg	europe/sofia	43.08124	25.62904	104770
pazardzhik-48-bg	europe/sofia	42.2	24.33333	138078
sofia-42-bg	europe/sofia	42.69751	23.32415	1152556
khaskovo-43-bg	europe/sofia	41.94028	25.56944	141918
burgas-39-bg	europe/sofia	42.50606	27.46781	236661
stara zagora-59-bg	europe/sofia	42.43278	25.64194	215870
sliven-56-bg	europe/sofia	42.68583	26.32917	120708
plovdiv-51-bg	europe/sofia	42.15	24.75	408446
pleven-50-bg	europe/sofia	43.41667	24.61667	140363
ruse-53-bg	europe/sofia	43.85639	25.97083	156238
banja luka-02-ba	europe/sarajevo	44.77583	17.18556	257453
sarajevo-01-ba	europe/sarajevo	43.84864	18.35644	730571
zenica-01-ba	europe/sarajevo	44.20169	17.90397	236928
tuzla-01-ba	europe/sarajevo	44.53842	18.66709	173903
mostar-01-ba	europe/sarajevo	43.34333	17.80806	104518
bihac-01-ba	europe/sarajevo	44.81694	15.87083	131905
east jerusalem-we-ps	asia/hebron	31.78336	35.23388	1092907
tulkarm-we-ps	asia/hebron	32.31037	35.02863	172993
gaza-gz-ps	asia/gaza	31.5	34.46667	1152380
dar kulayb-19-bh	asia/bahrain	26.06861	50.50389	118184
ar rifa'-18-bh	asia/bahrain	26.13	50.555	155297
manama-16-bh	asia/bahrain	26.21536	50.5832	178809
cochabamba-02-bo	america/la_paz	-17.3895	-66.1568	915608
sucre-01-bo	america/la_paz	-19.03332	-65.26274	224838
potosi-07-bo	america/la_paz	-19.58361	-65.75306	141251
la paz-04-bo	america/la_paz	-16.5	-68.15	812799
oruro-05-bo	america/la_paz	-17.98333	-67.15	224176
santa cruz de la sierra-08-bo	america/la_paz	-17.8	-63.16667	1420315
tarija-09-bo	america/la_paz	-21.53549	-64.72956	159269
shimonoseki-45-jp	asia/tokyo	33.95	130.95	487330
yamaguchi shi-45-jp	asia/tokyo	34.18583	131.47139	483272
iwakuni-45-jp	asia/tokyo	34.15	132.18333	212269
toyama shi-42-jp	asia/tokyo	36.69528	137.21139	847443
shimminatocho-43-jp	asia/tokyo	34.18333	135.2	909625
yokkaichi-23-jp	asia/tokyo	34.96667	136.61667	1108974
ise-23-jp	asia/tokyo	34.48333	136.7	120617
nabari-23-jp	asia/tokyo	34.61667	136.08333	149726
sendai shi-24-jp	asia/tokyo	38.26889	140.87194	1646181
miyazaki shi-25-jp	asia/tokyo	31.91111	131.42389	583018
nobeoka-25-jp	asia/tokyo	32.58333	131.66667	121949
nagano shi-26-jp	asia/tokyo	36.65139	138.18111	772096
matsumoto-26-jp	asia/tokyo	36.23333	137.96667	595902
iida-26-jp	asia/tokyo	35.51965	137.82074	107111
nagasaki shi-27-jp	asia/tokyo	32.74472	129.87361	947707
kochi shi-20-jp	asia/tokyo	33.55972	133.53111	406005
fukuoka shi-07-jp	asia/tokyo	33.60639	130.41806	3472017
omuta-07-jp	asia/tokyo	33.03333	130.45	155959
yukuhashi-07-jp	asia/tokyo	33.72873	130.983	201657
kyoto-22-jp	asia/tokyo	35.02107	135.75385	2023527
maizuru-22-jp	asia/tokyo	35.45	135.33333	220444
matsuyama shi-05-jp	asia/tokyo	33.83916	132.76574	630278
niihama-05-jp	asia/tokyo	33.95933	133.31672	160700
kofu shi-46-jp	asia/tokyo	35.66389	138.56833	380267
naha shi-47-jp	asia/tokyo	26.2125	127.68111	780723
iwaki-08-jp	asia/tokyo	37.05	140.88333	397992
koriyama-08-jp	asia/tokyo	37.4	140.38333	847739
gifu shi-09-jp	asia/tokyo	35.42291	136.76039	1180215
nara shi-28-jp	asia/tokyo	34.68505	135.80485	861834
niigata shi-29-jp	asia/tokyo	37.90222	139.02361	1083682
joetsu-29-jp	asia/tokyo	37.14828	138.23642	389802
nagaoka-29-jp	asia/tokyo	37.45	138.85	285168
tokyo-40-jp	asia/tokyo	35.6895	139.69171	13126393
tottori-41-jp	asia/tokyo	35.5	134.23333	202445
yonago-41-jp	asia/tokyo	35.43333	133.33333	177692
mito shi-14-jp	asia/tokyo	36.34139	140.44667	1597187
ryugasaki-14-jp	asia/tokyo	35.9	140.18333	446773
koga-14-jp	asia/tokyo	36.18333	139.71667	109578
akita shi-02-jp	asia/tokyo	39.71806	140.10333	707451
odate-02-jp	asia/tokyo	40.26861	140.56833	173089
nagoya shi-01-jp	asia/tokyo	35.18147	136.90641	5225206
toyohashi-01-jp	asia/tokyo	34.76667	137.38333	617138
aomori shi-03-jp	asia/tokyo	40.82444	140.74	600679
hachinohe-03-jp	asia/tokyo	40.5	141.5	281851
tokushima shi-39-jp	asia/tokyo	34.06583	134.55944	497873
utsunomiya shi-38-jp	asia/tokyo	36.56583	139.88361	1543604
fukui shi-06-jp	asia/tokyo	36.06443	136.22257	580833
kumamoto shi-21-jp	asia/tokyo	32.78972	130.74167	1016305
hiroshima shi-11-jp	asia/tokyo	34.39627	132.45937	1504403
fukuyama-11-jp	asia/tokyo	34.48333	133.36667	693304
maebashi shi-10-jp	asia/tokyo	36.39111	139.06083	1428202
kobe shi-13-jp	asia/tokyo	34.6913	135.183	4578614
ako-13-jp	asia/tokyo	34.75	134.4	149535
sapporo shi-12-jp	asia/tokyo	43.06417	141.34694	2503098
asahikawa-12-jp	asia/tokyo	43.76778	142.37028	492977
hakodate-12-jp	asia/tokyo	41.77583	140.73667	343836
kushiro-12-jp	asia/tokyo	42.975	144.37472	183612
tomakomai-12-jp	asia/tokyo	42.63694	141.60333	195610
obihiro-12-jp	asia/tokyo	42.91722	143.20444	214834
kitami-12-jp	asia/tokyo	43.80306	143.89083	178607
muroran-12-jp	asia/tokyo	42.31722	140.98806	131498
kanazawa shi-15-jp	asia/tokyo	36.59444	136.62556	769710
chiba shi-04-jp	asia/tokyo	35.60472	140.12333	4966652
tateyama-04-jp	asia/tokyo	34.98333	139.86667	101490
takamatsu shi-17-jp	asia/tokyo	34.34028	134.04333	580653
morioka shi-16-jp	asia/tokyo	39.70361	141.1525	482007
ichinoseki-16-jp	asia/tokyo	38.91667	141.13333	124251
miyako-16-jp	asia/tokyo	39.63667	141.9525	131469
yokohama shi-19-jp	asia/tokyo	35.44778	139.6425	8285653
osaka shi-32-jp	asia/tokyo	34.69374	135.50218	7266942
okayama shi-31-jp	asia/tokyo	34.66167	133.935	1428321
oita shi-30-jp	asia/tokyo	33.23806	131.6125	899250
shizuoka shi-37-jp	asia/tokyo	34.97694	138.38306	1832386
hamamatsu-37-jp	asia/tokyo	34.7	137.73333	823809
mishima-37-jp	asia/tokyo	35.11667	138.91667	309538
matsue shi-36-jp	asia/tokyo	35.47222	133.05056	303619
masuda-36-jp	asia/tokyo	34.66667	131.85	118923
otsu shi-35-jp	asia/tokyo	35.00444	135.86833	843056
saitama-34-jp	asia/tokyo	35.90807	139.65657	6700156
honjo-34-jp	asia/tokyo	36.23333	139.18333	141919
saga shi-33-jp	asia/tokyo	33.24932	130.2988	510089
kagoshima shi-18-jp	asia/tokyo	31.56018	130.55814	999671
yamagata shi-44-jp	asia/tokyo	38.24056	140.36333	617527
sakata-44-jp	asia/tokyo	38.91667	139.855	258488
bujumbura-24-bi	africa/bujumbura	-3.3822	29.3644	331700
spanish town-10-jm	america/jamaica	17.99107	-76.95742	294563
kingston-17-jm	america/jamaica	17.99702	-76.79358	937700
new kingston-08-jm	america/jamaica	18.00747	-76.78319	602510
`ajlun-20-jo	asia/amman	32.33385	35.75238	125557
az zarqa'-17-jo	asia/amman	32.07275	36.08796	1060902
irbid-18-jo	asia/amman	32.55556	35.85	436228
amman-16-jo	asia/amman	31.95522	35.94503	1594814
brasilia-07-br	america/sao_paulo	-15.77972	-47.92972	2207718
recife-30-br	america/recife	-8.05389	-34.88111	4195828
caruaru-30-br	america/recife	-8.28333	-35.97611	544833
petrolina-30-br	america/recife	-9.39861	-40.50083	194650
garanhuns-30-br	america/recife	-8.89028	-36.49278	163146
arcoverde-30-br	america/recife	-8.41889	-37.05389	137573
escada-30-br	america/recife	-8.35917	-35.22361	221314
timbauba-30-br	america/recife	-7.50528	-35.31833	177499
palmares-30-br	america/recife	-8.68333	-35.59167	117010
maceio-02-br	america/maceio	-9.66583	-35.73528	1216233
arapiraca-02-br	america/maceio	-9.7525	-36.66111	198409
macapa-03-br	america/belem	0.03889	-51.06639	422863
joinville-26-br	america/sao_paulo	-26.30444	-48.84556	682250
florianopolis-26-br	america/sao_paulo	-27.59667	-48.54917	705138
blumenau-26-br	america/sao_paulo	-26.91944	-49.06611	843724
sao jose-26-br	america/sao_paulo	-28.23333	-49.16667	389202
lages-26-br	america/sao_paulo	-27.81611	-50.32611	164676
criciuma-26-br	america/sao_paulo	-28.6775	-49.36972	279850
chapeco-26-br	america/sao_paulo	-27.09639	-52.61833	193114
sao bento do sul-26-br	america/sao_paulo	-26.25028	-49.37861	159592
cacador-26-br	america/sao_paulo	-26.77528	-51.015	106166
sao paulo-27-br	america/sao_paulo	-23.5475	-46.63611	18671817
campinas-27-br	america/sao_paulo	-22.90556	-47.06083	3016563
sao jose dos campos-27-br	america/sao_paulo	-23.17944	-45.88694	1232605
sorocaba-27-br	america/sao_paulo	-23.50167	-47.45806	1106621
ribeirao preto-27-br	america/sao_paulo	-21.1775	-47.81028	946604
santos-27-br	america/sao_paulo	-23.96083	-46.33361	1378000
sao jose do rio preto-27-br	america/sao_paulo	-20.81972	-49.37944	497976
piracicaba-27-br	america/sao_paulo	-22.72528	-47.64917	1084514
bauru-27-br	america/sao_paulo	-22.31472	-49.06056	506206
franca-27-br	america/sao_paulo	-20.53861	-47.40083	403021
marilia-27-br	america/sao_paulo	-22.21389	-49.94583	271535
presidente prudente-27-br	america/sao_paulo	-22.12556	-51.38889	305792
sao carlos-27-br	america/sao_paulo	-22.0175	-47.89083	591750
aracatuba-27-br	america/sao_paulo	-21.20889	-50.43278	370273
pindamonhangaba-27-br	america/sao_paulo	-22.92389	-45.46167	402160
mogi guacu-27-br	america/sao_paulo	-22.37222	-46.94222	474635
itapetininga-27-br	america/sao_paulo	-23.59167	-48.05306	126243
braganca paulista-27-br	america/sao_paulo	-22.95194	-46.54194	151171
jau-27-br	america/sao_paulo	-22.29639	-48.55778	233771
botucatu-27-br	america/sao_paulo	-22.88583	-48.445	129558
catanduva-27-br	america/sao_paulo	-21.13778	-48.97278	157887
barretos-27-br	america/sao_paulo	-20.55722	-48.56778	224346
ourinhos-27-br	america/sao_paulo	-22.97889	-49.87056	153674
caraguatatuba-27-br	america/sao_paulo	-23.62028	-45.41306	279109
itanhaem-27-br	america/sao_paulo	-24.18306	-46.78889	153415
assis-27-br	america/sao_paulo	-22.66167	-50.41222	154735
avare-27-br	america/sao_paulo	-23.09861	-48.92583	145074
leme-27-br	america/sao_paulo	-22.18556	-47.39028	107009
matao-27-br	america/sao_paulo	-21.60333	-48.36583	268405
votuporanga-27-br	america/sao_paulo	-20.42278	-49.97278	131794
lins-27-br	america/sao_paulo	-21.67861	-49.7425	113985
itapeva-27-br	america/sao_paulo	-23.98222	-48.87556	123724
tupa-27-br	america/sao_paulo	-21.93472	-50.51361	105461
mococa-27-br	america/sao_paulo	-21.46778	-47.00472	226321
teresina-20-br	america/fortaleza	-5.08917	-42.80194	809977
parnaiba-20-br	america/fortaleza	-2.90472	-41.77667	138008
rio de janeiro-21-br	america/sao_paulo	-22.90278	-43.2075	10070511
campos-21-br	america/sao_paulo	-21.75	-41.3	435816
volta redonda-21-br	america/sao_paulo	-22.52306	-44.10417	1003689
angra dos reis-21-br	america/sao_paulo	-23.00667	-44.31806	168753
nova friburgo-21-br	america/sao_paulo	-22.28194	-42.53111	411090
macae-21-br	america/sao_paulo	-22.37083	-41.78694	213110
araruama-21-br	america/sao_paulo	-22.87278	-42.34306	384849
itaperuna-21-br	america/sao_paulo	-21.205	-41.88778	175016
tres rios-21-br	america/sao_paulo	-22.11667	-43.20917	151970
manaus-04-br	america/manaus	-3.10194	-60.025	1598210
porto alegre-23-br	america/sao_paulo	-30.03306	-51.23	3384948
caxias do sul-23-br	america/sao_paulo	-29.16806	-51.17944	687791
pelotas-23-br	america/sao_paulo	-31.77194	-52.3425	508512
santa maria-23-br	america/sao_paulo	-29.68417	-53.80694	249219
passo fundo-23-br	america/sao_paulo	-28.26278	-52.40667	265806
uruguaiana-23-br	america/sao_paulo	-29.75472	-57.08833	123480
santa cruz do sul-23-br	america/sao_paulo	-29.7175	-52.42583	203909
ijui-23-br	america/sao_paulo	-28.38778	-53.91472	231490
lajeado-23-br	america/sao_paulo	-29.46694	-51.96139	147316
parobe-23-br	america/sao_paulo	-29.62861	-50.83472	161934
capao da canoa-23-br	america/sao_paulo	-29.74556	-50.00972	105258
vila velha-08-br	america/sao_paulo	-20.32972	-40.2925	1492020
cachoeiro de itapemirim-08-br	america/sao_paulo	-20.84889	-41.11278	287541
linhares-08-br	america/sao_paulo	-19.39111	-40.07222	105075
colatina-08-br	america/sao_paulo	-19.53944	-40.63056	178753
aracaju-28-br	america/maceio	-10.91111	-37.07167	857455
estancia-28-br	america/maceio	-11.26833	-37.43833	118248
goiania-29-br	america/sao_paulo	-16.67861	-49.25389	1930036
anapolis-29-br	america/sao_paulo	-16.32667	-48.95278	319587
luziania-29-br	america/sao_paulo	-16.2525	-47.95028	143601
planaltina-29-br	america/sao_paulo	-15.45278	-47.61417	170085
itumbiara-29-br	america/sao_paulo	-18.41917	-49.21528	105507
porto velho-24-br	america/porto_velho	-8.76194	-63.90389	306180
boa vista-25-br	america/boa_vista	2.81972	-60.67333	235150
rio branco-01-br	america/rio_branco	-9.97472	-67.81	257642
fortaleza-06-br	america/fortaleza	-3.71722	-38.54306	3153756
juazeiro do norte-06-br	america/fortaleza	-7.21306	-39.31528	375343
sobral-06-br	america/fortaleza	-3.68611	-40.34972	157996
iguatu-06-br	america/fortaleza	-6.35944	-39.29861	139592
itapipoca-06-br	america/fortaleza	-3.49444	-39.57861	149056
cascavel-06-br	america/fortaleza	-4.13306	-38.24194	130940
aracati-06-br	america/fortaleza	-4.56167	-37.76972	105548
cuiaba-14-br	america/cuiaba	-15.59611	-56.09667	771686
rondonopolis-14-br	america/cuiaba	-16.47083	-54.63556	152912
campo grande-11-br	america/campo_grande	-20.44278	-54.64639	729151
dourados-11-br	america/campo_grande	-22.22111	-54.80556	162202
corumba-11-br	america/campo_grande	-19.00917	-57.65333	112310
sao luis-13-br	america/fortaleza	-2.52972	-44.30278	945014
imperatriz-13-br	america/fortaleza	-5.52639	-47.49167	218106
timon-13-br	america/fortaleza	-5.09417	-42.83667	124427
codo-13-br	america/fortaleza	-4.45528	-43.88556	135292
bacabal-13-br	america/fortaleza	-4.29167	-44.79167	142171
santa ines-13-br	america/fortaleza	-3.66667	-45.38	107543
belo horizonte-15-br	america/sao_paulo	-19.92083	-43.93778	4770365
uberlandia-15-br	america/sao_paulo	-18.91861	-48.27722	660101
juiz de fora-15-br	america/sao_paulo	-21.76417	-43.35028	534929
montes claros-15-br	america/sao_paulo	-16.735	-43.86167	364493
uberaba-15-br	america/sao_paulo	-19.74833	-47.93194	260843
governador valadares-15-br	america/sao_paulo	-18.85111	-41.94944	250878
ipatinga-15-br	america/sao_paulo	-19.46833	-42.53667	481339
sete lagoas-15-br	america/sao_paulo	-19.46583	-44.24667	201334
divinopolis-15-br	america/sao_paulo	-20.13889	-44.88389	424450
pocos de caldas-15-br	america/sao_paulo	-21.78778	-46.56139	189613
patos de minas-15-br	america/sao_paulo	-18.57889	-46.51806	126234
barbacena-15-br	america/sao_paulo	-21.22583	-43.77361	155843
varginha-15-br	america/sao_paulo	-21.55139	-45.43028	319589
pouso alegre-15-br	america/sao_paulo	-22.23	-45.93639	165212
conselheiro lafaiete-15-br	america/sao_paulo	-20.66028	-43.78611	296016
teofilo otoni-15-br	america/sao_paulo	-17.8575	-41.50528	101170
itabira-15-br	america/sao_paulo	-19.61917	-43.22694	187853
passos-15-br	america/sao_paulo	-20.71889	-46.60972	155990
uba-15-br	america/sao_paulo	-21.12	-42.94278	258135
araxa-15-br	america/sao_paulo	-19.59333	-46.94056	101023
lavras-15-br	america/sao_paulo	-21.24528	-44.99972	163514
alfenas-15-br	america/sao_paulo	-21.42917	-45.94722	104408
pirapora-15-br	america/sao_paulo	-17.345	-44.94194	105465
lagoa da prata-15-br	america/sao_paulo	-20.0225	-45.54361	102261
natal-22-br	america/fortaleza	-5.795	-35.20944	1019357
mossoro-22-br	america/fortaleza	-5.1875	-37.34417	220377
joao pessoa-17-br	america/fortaleza	-7.115	-34.86306	960136
campina grande-17-br	america/fortaleza	-7.23056	-35.88111	384159
sousa-17-br	america/fortaleza	-6.75917	-38.22806	113591
belem-16-br	america/belem	-1.45583	-48.50444	1921358
santarem-16-br	america/santarem	-2.44306	-54.70833	189047
maraba-16-br	america/belem	-5.36861	-49.11778	167161
castanhal-16-br	america/belem	-1.29389	-47.92639	161542
abaetetuba-16-br	america/belem	-1.71806	-48.8825	126397
braganca-16-br	america/belem	-1.05361	-46.76556	121208
curitiba-18-br	america/sao_paulo	-25.42778	-49.27306	2614900
londrina-18-br	america/sao_paulo	-23.31028	-51.16278	863303
maringa-18-br	america/sao_paulo	-23.42528	-51.93861	532659
foz do iguacu-18-br	america/sao_paulo	-25.54778	-54.58806	308957
ponta grossa-18-br	america/sao_paulo	-25.095	-50.16194	372569
cascavel-18-br	america/sao_paulo	-24.95583	-53.45528	355017
guarapuava-18-br	america/sao_paulo	-25.39528	-51.45806	165991
paranagua-18-br	america/sao_paulo	-25.52	-48.50917	176071
umuarama-18-br	america/sao_paulo	-23.76639	-53.325	104744
campo mourao-18-br	america/sao_paulo	-24.04556	-52.38306	131395
pato branco-18-br	america/sao_paulo	-26.22861	-52.67056	139213
santo antonio da platina-18-br	america/sao_paulo	-23.295	-50.07722	121224
palmas-31-br	america/araguaina	-10.21278	-48.36028	196272
araguaina-31-br	america/araguaina	-7.19111	-48.20722	105019
salvador-05-br	america/bahia	-12.97111	-38.51083	3239837
feira de santana-05-br	america/bahia	-12.26667	-38.96667	657358
vitoria da conquista-05-br	america/bahia	-14.86611	-40.83944	276695
itabuna-05-br	america/bahia	-14.78556	-39.28028	469003
barreiras-05-br	america/bahia	-12.15278	-44.99	158292
jequie-05-br	america/bahia	-13.8575	-40.08361	207735
porto seguro-05-br	america/bahia	-16.44972	-39.06472	142718
alagoinhas-05-br	america/bahia	-12.13556	-38.41917	247753
santo antonio de jesus-05-br	america/bahia	-12.96889	-39.26139	227014
serrinha-05-br	america/bahia	-11.66417	-39.0075	116248
senhor do bonfim-05-br	america/bahia	-10.46139	-40.18944	112232
nassau-23-bs	america/nassau	25.05823	-77.34306	227940
sidon-06-lb	asia/beirut	33.56306	35.36889	298758
nabatiye et tahta-07-lb	asia/beirut	33.37889	35.48389	218433
beirut-04-lb	asia/beirut	33.88894	35.49442	3167839
djounie-05-lb	asia/beirut	33.98083	35.61778	117099
tripoli-09-lb	asia/beirut	34.43667	35.84972	249398
homyel'-02-by	europe/minsk	52.4345	30.9754	565434
mazyr-02-by	europe/minsk	52.0495	29.2456	149327
zhlobin-02-by	europe/minsk	52.8926	30.024	179039
hrodna-03-by	europe/minsk	53.6884	23.8258	317365
lida-03-by	europe/minsk	53.88333	25.29972	144484
novoye medvezhino-00-by	europe/minsk	53.88333	27.45	120000
brest-01-by	europe/minsk	52.09755	23.68775	351406
baranavichy-01-by	europe/minsk	53.1327	26.0139	168772
pinsk-01-by	europe/minsk	52.1229	26.0951	130777
mahilyow-06-by	europe/minsk	53.9168	30.3449	386700
babruysk-06-by	europe/minsk	53.1384	29.2214	255108
vitsyebsk-07-by	europe/minsk	55.1904	30.2049	342700
orsha-07-by	europe/minsk	54.5081	30.4172	125347
navapolatsk-07-by	europe/minsk	55.5318	28.5987	183143
malinovka-04-by	europe/minsk	53.8579	27.4374	105000
minsk-05-by	europe/minsk	53.9	27.56667	1783733
salihorsk-05-by	europe/minsk	52.7876	27.5415	163842
maladzyechna-05-by	europe/minsk	54.3167	26.854	131300
horad barysaw-05-by	europe/minsk	54.2279	28.505	161007
al sohar-02-om	asia/muscat	24.3643	56.74681	223973
as suwayq-02-om	asia/muscat	23.84944	57.43861	239013
nizwa-01-om	asia/muscat	22.93333	57.53333	162617
muscat-06-om	asia/muscat	23.61387	58.5922	1194303
salalah-08-om	asia/muscat	17.01505	54.09237	163140
`ibri-09-om	asia/muscat	23.22573	56.51572	118239
ternopil'-22-ua	europe/kiev	49.55589	25.60556	252638
chernihiv-02-ua	europe/kiev	51.50551	31.28488	307684
chernivtsi-03-ua	europe/kiev	48.29149	25.94034	236250
zaporizhzhya-26-ua	europe/zaporozhye	47.82289	35.19031	811229
melitopol'-26-ua	europe/zaporozhye	46.84891	35.36533	158000
berdyans'k-26-ua	europe/zaporozhye	46.7663	36.79882	118284
zhytomyr-27-ua	europe/kiev	50.26487	28.67669	408793
korosten'-27-ua	europe/kiev	50.95937	28.63855	108466
sevastopol'-20-ua	europe/simferopol	44.58883	33.5224	399200
kharkiv-07-ua	europe/kiev	49.98081	36.25272	1564870
dnipropetrovsk-04-ua	europe/kiev	48.45	34.98333	1403500
kryvyy rih-04-ua	europe/kiev	47.90966	33.38044	719767
nikopol'-04-ua	europe/kiev	47.57119	34.39637	180943
pavlohrad-04-ua	europe/kiev	48.53341	35.8705	115932
donets'k-05-ua	europe/kiev	48.023	37.80224	2044487
mariupol'-05-ua	europe/kiev	47.06667	37.5	481626
kramators'k-05-ua	europe/kiev	48.72305	37.55629	596751
shakhtersk-05-ua	europe/kiev	48.06252	38.51665	246831
kherson-08-ua	europe/kiev	46.65581	32.6178	365379
khmel'nyts'kyy-09-ua	europe/kiev	49.42161	26.99653	469144
kamieniec podolski-09-ua	europe/kiev	48.6845	26.58559	115836
shepetivka-09-ua	europe/kiev	50.18545	27.06365	152668
luts'k-24-ua	europe/kiev	50.75932	25.34244	230170
kovel'-24-ua	europe/kiev	51.21526	24.70867	104656
uzhhorod-25-ua	europe/uzhgorod	48.61667	22.3	199511
cherkasy-01-ua	europe/kiev	49.42854	32.06207	407883
ivano frankivs'k-06-ua	europe/kiev	48.9215	24.70972	353833
sumy-21-ua	europe/kiev	50.9216	34.80029	339975
konotop-21-ua	europe/kiev	51.24032	33.20263	135913
shostka-21-ua	europe/kiev	51.86296	33.4698	120819
simferopol'-11-ua	europe/simferopol	44.95719	34.11079	461317
kerch-11-ua	europe/simferopol	45.3607	36.4706	152195
yevpatoriya-11-ua	europe/simferopol	45.20091	33.36655	105223
yalta-11-ua	europe/simferopol	44.50013	34.16148	109509
nyzhn'ohirs'kyy-11-ua	europe/simferopol	45.44789	34.73839	114265
kirovohrad-10-ua	europe/kiev	48.5132	32.2597	277772
oleksandriya-10-ua	europe/kiev	48.66961	33.11593	150946
bila tserkva-13-ua	europe/kiev	49.80939	30.11209	339015
brovary-13-ua	europe/kiev	50.51809	30.80671	316468
kiev-12-ua	europe/kiev	50.45466	30.5238	2514227
l'viv-15-ua	europe/kiev	49.83826	24.02324	733796
chervonograd-15-ua	europe/kiev	50.39105	24.23514	104451
drogobych-15-ua	europe/kiev	49.34991	23.50561	259398
luhans'k-14-ua	europe/zaporozhye	48.56705	39.31706	827402
syeverodonets'k-14-ua	europe/zaporozhye	48.94832	38.49166	457053
krasnyy luch-14-ua	europe/zaporozhye	48.13954	38.93715	205205
odessa-17-ua	europe/kiev	46.47747	30.73262	1130861
izmayil-17-ua	europe/kiev	45.34929	28.84079	140666
mykolayiv-16-ua	europe/kiev	46.96591	31.9974	510840
pervomays'k-16-ua	europe/kiev	48.04433	30.85073	110176
rivne-19-ua	europe/kiev	50.62308	26.22743	316493
poltava-18-ua	europe/kiev	49.59373	34.54073	335073
kremenchuk-18-ua	europe/kiev	49.09725	33.41972	279234
lubny-18-ua	europe/kiev	50.01625	32.99694	110066
vinnytsya-23-ua	europe/kiev	49.23278	28.48097	407390
molepolole-06-bw	africa/gaborone	-24.40659	25.49508	127398
gaborone-09-bw	africa/gaborone	-24.65451	25.90859	229861
mitrovice-15-xk	europe/belgrade	42.88333	20.86667	107045
prizren-21-xk	europe/belgrade	42.21389	20.73972	171464
pristina-20-xk	europe/belgrade	42.67272	21.16688	550000
san pedro-76-ci	africa/abidjan	4.74851	-6.6363	196751
divo-88-ci	africa/abidjan	5.83739	-5.35723	165922
agboville-74-ci	africa/abidjan	5.92801	-4.21319	143654
abidjan-82-ci	africa/abidjan	5.30966	-4.01266	4909207
bouake-90-ci	africa/abidjan	7.69385	-5.03031	642190
daloa-80-ci	africa/abidjan	6.87736	-6.45022	265965
yamoussoukro-81-ci	africa/abidjan	6.82055	-5.27674	233535
abengourou-85-ci	africa/abidjan	6.72972	-3.49639	104020
korhogo-87-ci	africa/abidjan	9.45803	-5.62961	167359
gagnoa-79-ci	africa/abidjan	6.13193	-5.9506	123184
man-78-ci	africa/abidjan	7.41251	-7.55383	179921
lausanne-vd-ch	europe/zurich	46.516	6.63282	253225
geneve-ge-ch	europe/zurich	46.20222	6.14569	297776
bern-be246-ch	europe/zurich	46.94809	7.44744	158827
basel-bs-ch	europe/zurich	47.5584	7.57327	184488
sankt gallen-sg-ch	europe/zurich	47.42391	9.37477	156854
winterthur-zh110-ch	europe/zurich	47.5	8.75	139880
zurich-zh112-ch	europe/zurich	47.36667	8.55	874800
medellin-02-co	america/bogota	6.25184	-75.56359	3214697
apartado-02-co	america/bogota	7.88299	-76.62587	206016
bucaramanga-26-co	america/bogota	7.12539	-73.1198	1018940
barrancabermeja-26-co	america/bogota	7.06528	-73.85472	191403
sincelejo-27-co	america/bogota	9.30472	-75.39778	413306
pasto-20-co	america/bogota	1.21361	-77.28111	417481
cucuta-21-co	america/bogota	7.89391	-72.50782	845010
barranquilla-04-co	america/bogota	10.96389	-74.79639	2061898
armenia-23-co	america/bogota	4.53389	-75.68111	492599
florencia-08-co	america/bogota	1.61438	-75.60623	130337
popayan-09-co	america/bogota	2.43823	-76.61316	288270
puerto tejada-09-co	america/bogota	3.23114	-76.41668	111051
ibague-28-co	america/bogota	4.43889	-75.23222	442604
libano-28-co	america/bogota	4.9218	-75.06232	117210
cali-29-co	america/bogota	3.43722	-76.5225	2930951
buenaventura-29-co	america/bogota	3.8801	-77.03116	265229
tulua-29-co	america/bogota	4.08466	-76.19536	431288
cartago-29-co	america/bogota	4.74639	-75.91167	158286
pereira-24-co	america/bogota	4.81333	-75.69611	727162
monteria-12-co	america/bogota	8.74798	-75.88143	407468
montelibano-12-co	america/bogota	7.98288	-75.42293	107602
valledupar-10-co	america/bogota	10.46314	-73.25322	359715
santa marta-38-co	america/bogota	11.24079	-74.19904	520092
fundacion-38-co	america/bogota	10.52066	-74.18504	136272
maicao-17-co	america/bogota	11.38321	-72.24321	130348
neiva-16-co	america/bogota	2.9273	-75.28188	375423
villavicencio-19-co	america/bogota	4.142	-73.62664	362344
manizales-37-co	america/bogota	5.06889	-75.51738	530148
sogamoso-36-co	america/bogota	5.71434	-72.93391	218591
tunja-36-co	america/bogota	5.53528	-73.36778	117479
cartagena-35-co	america/bogota	10.39972	-75.51444	1058600
magangue-35-co	america/bogota	9.24202	-74.75467	131174
el carmen de bolivar-35-co	america/bogota	9.7174	-75.12023	121242
bogota-34-co	america/bogota	4.60971	-74.08175	7102602
soacha-33-co	america/bogota	4.57937	-74.21682	742015
girardot-33-co	america/bogota	4.29866	-74.80468	130289
zipaquira-33-co	america/bogota	5.02208	-74.00481	155117
puyang-02-cn	asia/shanghai	29.45679	119.88872	4136649
hangzhou-02-cn	asia/shanghai	30.29365	120.16142	2209302
wenzhou-02-cn	asia/shanghai	27.99942	120.66682	930681
shangyu-02-cn	asia/shanghai	30.01556	120.87111	1460460
ningbo-02-cn	asia/shanghai	29.87819	121.54945	858499
guli-02-cn	asia/shanghai	28.88162	120.03308	634946
jiaojiang-02-cn	asia/shanghai	28.68028	121.44278	1269512
jiaxing-02-cn	asia/shanghai	30.7522	120.75	673384
huzhou-02-cn	asia/shanghai	30.8703	120.0933	222073
shenjiamen-02-cn	asia/shanghai	29.95762	122.29802	179813
tai'an-25-cn	asia/shanghai	36.18528	117.12	5700714
jinan-25-cn	asia/shanghai	36.66833	116.99722	2266722
qingdao-25-cn	asia/shanghai	36.09861	120.37194	1953660
zhu cheng city-25-cn	asia/shanghai	35.99502	119.40259	1109968
yantai-25-cn	asia/shanghai	37.53333	121.4	841891
zibo-25-cn	asia/shanghai	36.79056	118.06333	1289640
jining-25-cn	asia/shanghai	35.405	116.58139	1003840
weifang-25-cn	asia/shanghai	36.71	119.10194	670246
dezhou-25-cn	asia/shanghai	37.44861	116.2925	379555
dongying-25-cn	asia/shanghai	37.45639	118.48556	422343
linyi-25-cn	asia/shanghai	35.06306	118.34278	567013
heze-25-cn	asia/shanghai	35.24306	115.44111	312808
rizhao-25-cn	asia/shanghai	35.4275	119.45528	246387
liaocheng-25-cn	asia/shanghai	36.44389	115.96472	442901
xintai-25-cn	asia/shanghai	35.90056	117.75194	513965
zaozhuang-25-cn	asia/shanghai	34.86472	117.55417	555768
laiyang-25-cn	asia/shanghai	36.97583	120.71361	416831
weihai-25-cn	asia/shanghai	37.50167	122.11361	359482
gaomi-25-cn	asia/shanghai	36.38333	119.75278	241870
linqing-25-cn	asia/shanghai	36.84556	115.71167	110046
zhaoyuan-25-cn	asia/shanghai	37.35917	120.39639	251288
yishui-25-cn	asia/shanghai	35.78472	118.62806	229948
shancheng-25-cn	asia/shanghai	34.79528	116.08167	136824
xi'an-26-cn	asia/chongqing	34.25833	108.92861	4395981
tongchuan-26-cn	asia/chongqing	35.08056	109.08972	284494
weinan-26-cn	asia/chongqing	34.50355	109.50891	172321
hanzhong-26-cn	asia/chongqing	33.07278	107.03028	145986
ankang-26-cn	asia/chongqing	32.68	109.01722	132654
hefei-01-cn	asia/shanghai	31.86389	117.28083	1388904
huainan-01-cn	asia/shanghai	32.62639	116.99694	1730918
huaibei-01-cn	asia/shanghai	33.97444	116.79167	1182341
wuhu-01-cn	asia/shanghai	31.33728	118.37351	567859
anqing-01-cn	asia/shanghai	30.50917	117.05056	507036
wusong-01-cn	asia/shanghai	30.95	117.78333	312588
chuzhou-01-cn	asia/shanghai	32.32194	118.29778	280582
bozhou-01-cn	asia/shanghai	33.87722	115.77028	174140
fuyang-01-cn	asia/shanghai	32.9	115.81667	170023
jieshou-01-cn	asia/shanghai	33.26338	115.36108	141993
chaohu-01-cn	asia/shanghai	31.6	117.86667	138463
xuanzhou-01-cn	asia/shanghai	30.9525	118.75528	127758
wuyang-01-cn	asia/shanghai	31.9925	116.24722	140974
huangshan-01-cn	asia/shanghai	29.71139	118.3125	137212
ordos-20-cn	asia/chongqing	39.6086	109.78157	2040462
baotou-20-cn	asia/chongqing	40.65222	109.82222	1372125
hohhot-20-cn	asia/chongqing	40.81056	111.65222	774477
chifeng-20-cn	asia/shanghai	42.26833	118.96361	474554
tongliao-20-cn	asia/shanghai	43.6125	122.26528	261110
jining-20-cn	asia/chongqing	41.0275	113.10583	258757
wuhai-20-cn	asia/chongqing	39.66472	106.81222	348349
hailar-20-cn	asia/shanghai	49.2	119.7	211066
ulanhot-20-cn	asia/shanghai	46.08333	122.08333	165846
jagdaqi-20-cn	asia/shanghai	50.41667	124.11667	197342
zalantun-20-cn	asia/shanghai	48.0	122.71667	132224
xilin hot-20-cn	asia/shanghai	43.96667	116.03333	120965
yakeshi-20-cn	asia/shanghai	49.28333	120.73333	116284
jalai nur-20-cn	asia/shanghai	49.45	117.7	162636
fuzhou-07-cn	asia/shanghai	26.06139	119.30611	1316167
zhangzhou-07-cn	asia/shanghai	24.51333	117.65556	1236543
putian-07-cn	asia/shanghai	25.43944	119.01028	436460
sanming-07-cn	asia/shanghai	26.24861	117.61861	209444
quanzhou-07-cn	asia/shanghai	24.91389	118.58583	434280
nanping-07-cn	asia/shanghai	26.645	118.17361	230861
shaowu-07-cn	asia/shanghai	27.34089	117.4831	112585
chengyang-07-cn	asia/shanghai	27.08917	119.64528	136223
nanjing-04-cn	asia/shanghai	32.06167	118.77778	3329047
suzhou-04-cn	asia/shanghai	31.30408	120.59538	3768892
tongshan-04-cn	asia/shanghai	34.18045	117.15707	1199193
changzhou-04-cn	asia/shanghai	31.77358	119.95401	1232121
nantong-04-cn	asia/shanghai	32.03028	120.87472	901254
zhenjiang-04-cn	asia/shanghai	32.21086	119.45508	1256203
yancheng-04-cn	asia/shanghai	33.38556	120.12528	857846
taizhou-04-cn	asia/shanghai	32.49069	119.90812	682731
huaiyin-04-cn	asia/shanghai	33.58861	119.01917	692860
xinpu-04-cn	asia/shanghai	34.59972	119.15944	451542
dongtai-04-cn	asia/shanghai	32.85231	120.30947	216906
pizhou-04-cn	asia/shanghai	34.31139	117.95028	144071
licheng-04-cn	asia/shanghai	31.42813	119.48353	128646
shanghai-23-cn	asia/shanghai	31.22222	121.45806	14738730
harbin-08-cn	asia/harbin	45.75	126.65	3483652
qiqihar-08-cn	asia/harbin	47.34083	123.96722	1147708
hegang-08-cn	asia/harbin	47.4	130.36667	785416
mudanjiang-08-cn	asia/harbin	44.58333	129.6	819456
shuangyashan-08-cn	asia/harbin	46.63611	131.15389	866587
jiamusi-08-cn	asia/harbin	46.83333	130.35	549549
jixi-08-cn	asia/harbin	45.3	130.96667	834872
qitaihe-08-cn	asia/harbin	45.8	130.85	440293
suihua-08-cn	asia/harbin	46.64056	126.99694	394198
ranghulu-08-cn	asia/harbin	46.65	124.86667	966424
yichun-08-cn	asia/harbin	47.7	128.9	234164
zhaodong-08-cn	asia/harbin	46.08333	125.98333	226934
shuangcheng-08-cn	asia/harbin	45.35	126.28333	130710
nancha-08-cn	asia/harbin	47.13333	129.26667	178685
hailun-08-cn	asia/harbin	47.45	126.93333	167005
tieli-08-cn	asia/harbin	46.95	128.05	109636
heihe-08-cn	asia/harbin	50.24413	127.49016	109427
nehe-08-cn	asia/harbin	48.48333	124.83333	108253
longjiang-08-cn	asia/harbin	47.33028	123.18361	168515
wuchang-08-cn	asia/harbin	44.91428	127.15001	152336
linkou-08-cn	asia/harbin	45.3	130.28333	143924
baiquan-08-cn	asia/harbin	47.58333	126.08333	129841
zhaozhou-08-cn	asia/harbin	45.68333	125.31667	121743
binzhou-08-cn	asia/harbin	45.75281	127.47986	117203
zhumadian-09-cn	asia/shanghai	32.97944	114.02944	8323302
kaifeng-09-cn	asia/shanghai	34.7986	114.30742	4800000
zhengzhou-09-cn	asia/shanghai	34.75778	113.64861	2014125
xinyang-09-cn	asia/shanghai	32.12278	114.06556	1658613
luoyang-09-cn	asia/shanghai	34.68361	112.45361	1446614
pingdingshan-09-cn	asia/shanghai	33.73847	113.30119	1043469
anyang-09-cn	asia/shanghai	36.09944	114.32889	1084864
xinxiang-09-cn	asia/shanghai	35.30889	113.86722	743601
puyang-09-cn	asia/shanghai	35.70278	115.00528	722959
jiaozuo-09-cn	asia/shanghai	35.23972	113.23306	578285
xuchang-09-cn	asia/shanghai	34.01667	113.81667	449258
luohe-09-cn	asia/shanghai	33.57167	114.03528	417356
zhoukou-09-cn	asia/shanghai	33.63333	114.63333	533887
nanyang-09-cn	asia/shanghai	32.99472	112.53278	320046
shangqiu-09-cn	asia/shanghai	34.45	115.65	181218
jishui-09-cn	asia/shanghai	33.73333	115.4	142951
xinye-09-cn	asia/shanghai	32.51861	112.35222	120971
tianjin-28-cn	asia/shanghai	39.14222	117.17667	4515676
hangu-28-cn	asia/shanghai	39.24889	117.78917	208369
dayan-29-cn	asia/chongqing	26.86879	100.22072	1137600
kunming-29-cn	asia/chongqing	25.03889	102.71833	1374809
kaiyuan-29-cn	asia/chongqing	23.69767	103.30372	334558
qujing-29-cn	asia/chongqing	25.48333	103.78333	146015
dali-29-cn	asia/chongqing	25.7	100.18333	134040
zhaotong-29-cn	asia/chongqing	27.31667	103.71667	109400
yuxi-29-cn	asia/chongqing	24.355	102.54222	103829
zhongshu-29-cn	asia/chongqing	24.51667	103.76667	164235
kaihua-29-cn	asia/chongqing	23.3687	104.28	127973
lhasa-14-cn	asia/urumqi	29.65	91.1	118721
changchun-05-cn	asia/harbin	43.88	125.32278	2657990
jilin-05-cn	asia/harbin	43.85083	126.56028	1881977
siping-05-cn	asia/harbin	43.16333	124.36861	617193
liaoyuan-05-cn	asia/harbin	42.90361	125.13583	533069
yanji-05-cn	asia/harbin	42.9075	129.50778	522861
baicheng-05-cn	asia/harbin	45.61667	122.81667	497549
baishan-05-cn	asia/harbin	41.94306	126.42861	445734
jiutai-05-cn	asia/harbin	44.1525	125.83278	283933
dunhua-05-cn	asia/harbin	43.3725	128.2425	269486
gongzhuling-05-cn	asia/harbin	43.50075	124.81979	140909
huadian-05-cn	asia/harbin	42.96333	126.74778	139047
fuyu-05-cn	asia/harbin	45.18333	124.81667	252315
yushu-05-cn	asia/harbin	44.8	126.53333	124736
jiaohe-05-cn	asia/harbin	43.72861	127.34472	180010
jishu-05-cn	asia/harbin	44.31667	126.8	181408
meihekou-05-cn	asia/harbin	42.52722	125.67528	308056
panshi-05-cn	asia/harbin	42.94222	126.05611	137715
taiyuan-24-cn	asia/shanghai	37.86944	112.56028	2958404
datong-24-cn	asia/shanghai	40.09361	113.29139	1052678
changzhi-24-cn	asia/shanghai	35.20889	111.73861	699514
yangquan-24-cn	asia/shanghai	37.8575	113.56333	413394
jincheng-24-cn	asia/shanghai	35.50222	112.83278	332650
linfen-24-cn	asia/shanghai	36.08889	111.51889	304869
yuncheng-24-cn	asia/shanghai	35.02306	110.99278	201950
xinzhou-24-cn	asia/shanghai	38.40917	112.73333	236886
jiexiu-24-cn	asia/shanghai	37.02444	111.9125	119178
nanchang-03-cn	asia/shanghai	28.68333	115.88333	1927780
pingxiang-03-cn	asia/shanghai	27.61667	113.85	372123
shangrao-03-cn	asia/shanghai	28.45322	117.9686	318769
jingdezhen-03-cn	asia/shanghai	29.2947	117.20789	310565
jiujiang-03-cn	asia/shanghai	29.73333	115.98333	258807
ji'an-03-cn	asia/shanghai	27.11716	114.97927	245000
yichun-03-cn	asia/shanghai	27.83333	114.4	210647
xining-06-cn	asia/chongqing	36.61667	101.76667	767531
yinchuan-21-cn	asia/chongqing	38.46806	106.27306	475101
shizuishan-21-cn	asia/chongqing	39.23333	106.76944	347215
yueyang-11-cn	asia/shanghai	29.33333	113.09194	5000000
changsha-11-cn	asia/shanghai	28.2	112.96667	3512797
liuyang-11-cn	asia/shanghai	28.15	113.63333	1380000
hengyang-11-cn	asia/shanghai	26.88806	112.615	759602
changde-11-cn	asia/shanghai	29.04638	111.6783	517780
fenghuang-11-cn	asia/shanghai	27.93557	109.59961	472332
yiyang-11-cn	asia/shanghai	28.58917	112.32833	268753
chenzhou-11-cn	asia/shanghai	25.8	113.03333	179038
loudi-11-cn	asia/shanghai	27.73444	111.99444	287968
leiyang-11-cn	asia/shanghai	26.40238	112.85908	129116
huaihua-11-cn	asia/shanghai	27.54944	109.95917	241942
lengshuijiang-11-cn	asia/shanghai	27.68806	111.42944	190632
lengshuitan-11-cn	asia/shanghai	26.4111	111.59559	180377
jinshi-11-cn	asia/shanghai	29.60487	111.87012	140675
shijiazhuang-10-cn	asia/shanghai	38.04139	114.47861	2650896
tangshan-10-cn	asia/shanghai	39.63333	118.18333	1969943
handan-10-cn	asia/shanghai	36.60056	114.46778	1744856
baoding-10-cn	asia/shanghai	38.85111	115.49028	995652
qinhuangdao-10-cn	asia/shanghai	39.93167	119.58833	890194
langfang-10-cn	asia/shanghai	39.50972	116.69472	720119
zhangjiakou-10-cn	asia/shanghai	40.81	114.87944	1066024
xingtai-10-cn	asia/shanghai	37.06306	114.49417	611739
cangzhou-10-cn	asia/shanghai	38.31667	116.86667	590726
hengshui-10-cn	asia/shanghai	37.73222	115.70111	602267
chengde-10-cn	asia/shanghai	40.9725	117.93611	449325
dingzhou-10-cn	asia/shanghai	38.51306	114.99556	152934
urunchi-13-cn	asia/urumqi	43.80096	87.60046	1707001
shihezi-13-cn	asia/urumqi	44.3	86.03333	572772
aksu-13-cn	asia/kashgar	41.12306	80.26444	340020
kashi-13-cn	asia/kashgar	39.45472	75.97972	274717
aral-13-cn	asia/kashgar	40.51556	81.26361	260000
turpan-13-cn	asia/urumqi	42.93333	89.16667	254900
korla-13-cn	asia/urumqi	41.75972	86.14694	179465
altay-13-cn	asia/urumqi	47.86667	88.11667	139341
hami-13-cn	asia/urumqi	42.8	93.45	137072
hotan-13-cn	asia/kashgar	37.09972	79.92694	114000
wuhan-12-cn	asia/shanghai	30.58333	114.26667	4401388
shiyan-12-cn	asia/shanghai	32.6475	110.77806	3868055
huangshi-12-cn	asia/shanghai	30.20417	115.07761	1209676
shashi-12-cn	asia/shanghai	30.30722	112.24472	843174
yichang-12-cn	asia/shanghai	30.71444	111.28472	476725
xiangyang-12-cn	asia/shanghai	32.0422	112.14479	607587
suizhou-12-cn	asia/shanghai	31.71111	113.36306	414367
yingcheng-12-cn	asia/shanghai	30.95	113.55	660333
laohekou-12-cn	asia/shanghai	32.38583	111.66778	419158
xiantao-12-cn	asia/shanghai	30.38333	113.4	710495
wuxue-12-cn	asia/shanghai	29.85058	115.5525	220661
zaoyang-12-cn	asia/shanghai	32.12722	112.75417	184509
xianning-12-cn	asia/shanghai	29.88333	114.21667	312385
xindi-12-cn	asia/shanghai	29.81667	113.46667	175761
jingmen-12-cn	asia/shanghai	31.03361	112.20472	276633
zhicheng-12-cn	asia/shanghai	30.29556	111.50472	159383
guangshui-12-cn	asia/shanghai	31.6199	113.9978	154771
macheng-12-cn	asia/shanghai	31.17833	115.03194	205133
xiulin-12-cn	asia/shanghai	29.71667	112.4	122411
lanzhou-15-cn	asia/chongqing	36.05639	103.79222	3200000
linxia-15-cn	asia/chongqing	35.60028	103.20639	202402
baiyin-15-cn	asia/chongqing	36.55833	104.20806	188533
jinchang-15-cn	asia/chongqing	38.49528	102.17389	144363
jiayuguan-15-cn	asia/chongqing	39.81667	98.3	279897
pingliang-15-cn	asia/chongqing	35.53917	106.68611	108156
beijing-22-cn	asia/shanghai	39.9075	116.39723	8331170
nanning-16-cn	asia/chongqing	22.81667	108.31667	865478
guilin-16-cn	asia/chongqing	25.28194	110.28639	649352
yangshuo-16-cn	asia/chongqing	24.78081	110.48967	300000
beihai-16-cn	asia/chongqing	21.48333	109.1	360991
wuzhou-16-cn	asia/chongqing	23.48333	111.31667	265846
yulin-16-cn	asia/chongqing	22.63333	110.15	203333
qinzhou-16-cn	asia/chongqing	21.95	108.61667	100996
guiping-16-cn	asia/chongqing	23.3925	110.08139	133549
nandu-16-cn	asia/chongqing	22.8525	110.82333	118697
chongqing-33-cn	asia/chongqing	29.56278	106.55278	4221616
wanxian-33-cn	asia/chongqing	30.81544	108.37089	188980
fuling-33-cn	asia/chongqing	29.70222	107.39194	166507
nanchong-32-cn	asia/chongqing	30.79508	106.08474	7354368
chengdu-32-cn	asia/chongqing	30.66667	104.06667	4011234
zigong-32-cn	asia/chongqing	29.34162	104.77689	1295256
dadukou-32-cn	asia/chongqing	26.5479	101.70539	461513
mianyang-32-cn	asia/chongqing	31.45934	104.75424	391361
yibin-32-cn	asia/chongqing	28.76667	104.62383	306691
guangyuan-32-cn	asia/chongqing	32.44202	105.823	213365
leshan-32-cn	asia/chongqing	29.56228	103.76386	228058
deyang-32-cn	asia/chongqing	31.13019	104.38198	152194
dazhou-32-cn	asia/chongqing	31.21592	107.50092	130749
xichang-32-cn	asia/chongqing	27.89642	102.26342	126787
suining-32-cn	asia/chongqing	30.50802	105.57332	124924
kangding-32-cn	asia/chongqing	30.05127	101.96033	100000
nanlong-32-cn	asia/chongqing	31.35333	106.06309	123947
haikou-31-cn	asia/chongqing	20.04583	110.34167	1062212
sanya-31-cn	asia/chongqing	18.24306	109.505	144753
guangzhou-30-cn	asia/shanghai	23.11667	113.25	4585533
shenzhen-30-cn	asia/shanghai	22.54554	114.0683	3126701
yunfu-30-cn	asia/chongqing	22.93056	112.0373	3070589
zhongshan-30-cn	asia/urumqi	21.32256	110.58291	3627400
shantou-30-cn	asia/shanghai	23.36814	116.71479	3427545
shaoguan-30-cn	asia/shanghai	24.8	113.58333	866626
jiangmen-30-cn	asia/shanghai	22.58333	113.08333	1215294
zhuhai-30-cn	asia/shanghai	22.27694	113.56778	501199
yangjiang-30-cn	asia/chongqing	21.85	111.96667	635011
dongguan-30-cn	asia/shanghai	23.04889	113.74472	864618
huizhou-30-cn	asia/shanghai	23.08333	114.4	525976
donghai-30-cn	asia/shanghai	22.94594	115.64204	622043
gaozhou-30-cn	asia/urumqi	21.93924	110.84607	264328
qingyuan-30-cn	asia/shanghai	23.7	113.03333	151287
meizhou-30-cn	asia/shanghai	24.29769	116.10724	144212
hepo-30-cn	asia/shanghai	23.43077	115.82991	249261
huicheng-30-cn	asia/shanghai	23.03845	116.28988	125919
encheng-30-cn	asia/chongqing	22.18325	112.30615	110921
huaicheng-30-cn	asia/shanghai	23.90513	112.19314	175423
xiongzhou-30-cn	asia/shanghai	25.11667	114.3	152046
shenyang-19-cn	asia/shanghai	41.79222	123.43278	5294384
dalian-19-cn	asia/shanghai	38.91222	121.60222	2388879
anshan-19-cn	asia/shanghai	41.12361	122.99	2384589
benxi-19-cn	asia/shanghai	41.28861	123.765	1056711
fuxin-19-cn	asia/shanghai	42.01556	121.65889	746406
dandong-19-cn	asia/shanghai	40.12917	124.39472	811533
panshan-19-cn	asia/shanghai	41.18806	122.04944	625040
jinzhou-19-cn	asia/shanghai	41.10778	121.14167	1130736
yingkou-19-cn	asia/shanghai	40.66482	122.22833	671382
chaoyang-19-cn	asia/shanghai	41.57028	120.45861	565004
tieling-19-cn	asia/shanghai	42.29306	123.84139	446369
wafangdian-19-cn	asia/shanghai	39.61833	122.00806	354868
lingyuan-19-cn	asia/shanghai	41.24	119.40111	156954
guiyang-18-cn	asia/chongqing	26.58333	106.71667	1171633
zunyi-18-cn	asia/chongqing	27.68667	106.90722	466292
anshun-18-cn	asia/chongqing	26.25	105.93333	351936
duyun-18-cn	asia/chongqing	26.26667	107.51667	150049
yaounde-11-cm	africa/douala	3.86667	11.51667	1409587
nkoteng-11-cm	africa/douala	4.51667	12.03333	107190
ngaoundere-10-cm	africa/douala	7.31667	13.58333	231357
garoua-13-cm	africa/douala	9.3	13.4	461495
kousseri-12-cm	africa/douala	12.07689	15.03063	435547
maroua-12-cm	africa/douala	10.59095	14.31592	336893
mokolo-12-cm	africa/douala	10.73978	13.80188	275239
bamenda-07-cm	africa/douala	5.95266	10.15824	578786
bertoua-04-cm	africa/douala	4.57728	13.68459	218111
douala-05-cm	africa/douala	4.04827	9.70428	1357325
edea-05-cm	africa/douala	3.8	10.13333	203149
loum-05-cm	africa/douala	4.7182	9.7351	403149
bafoussam-08-cm	africa/douala	5.47366	10.41786	728338
kumba-09-cm	africa/douala	4.6363	9.4469	175797
limbe-09-cm	africa/douala	4.0242	9.2149	240598
temuco-0491-cl	america/santiago	-38.73333	-72.6	278485
punta arenas-10121-cl	america/santiago	-53.15	-70.91667	117430
valdivia-17141-cl	america/santiago	-39.81422	-73.24589	133419
antofagasta-0321-cl	america/santiago	-23.65	-70.4	309832
calama-0322-cl	america/santiago	-22.46667	-68.93333	143084
puente alto-12132-cl	america/santiago	-33.61667	-70.58333	510417
santiago-12131-cl	america/santiago	-33.45694	-70.64827	5142789
penaflor-12136-cl	america/santiago	-33.61667	-70.91667	140349
san bernardo-12134-cl	america/santiago	-33.6	-70.71667	338065
puerto montt-14101-cl	america/santiago	-41.46985	-72.94474	201951
osorno-14103-cl	america/santiago	-40.56667	-73.15	135773
linares-1174-cl	america/santiago	-35.85	-71.6	118866
curico-1173-cl	america/santiago	-34.98333	-71.23333	131213
talca-1171-cl	america/santiago	-35.43333	-71.66667	197479
rancagua-0861-cl	america/santiago	-34.17083	-70.74444	324263
copiapo-0531-cl	america/santiago	-27.36667	-70.33333	129280
los angeles-0683-cl	america/santiago	-37.46667	-72.35	203697
talcahuano-0681-cl	america/santiago	-36.71667	-73.11667	786418
chillan-0684-cl	america/santiago	-36.60664	-72.10344	181913
san antonio-0156-cl	america/santiago	-33.59333	-71.62167	102526
quillota-0155-cl	america/santiago	-32.88333	-71.26667	116885
coquimbo-0741-cl	america/santiago	-29.95333	-71.34361	315838
vina del mar-0151-cl	america/santiago	-33.02457	-71.55183	576999
arica-16151-cl	america/santiago	-18.475	-70.30417	185999
iquique-1511-cl	america/santiago	-20.22083	-70.14306	227499
quilpue-0158-cl	america/santiago	-33.045	-71.44944	263459
durres-42-al	europe/tirane	41.32306	19.44139	122034
fier cifci-44-al	europe/tirane	40.71667	19.56667	139971
tirana-50-al	europe/tirane	41.3275	19.81889	374801
elbasan-43-al	europe/tirane	41.1125	20.08222	100903
vancouver-02-ca	america/vancouver	49.24966	-123.11934	3464913
okanagan-02-ca	america/vancouver	50.36386	-119.34997	361080
victoria-02-ca	america/vancouver	48.43294	-123.3693	334283
abbotsford-02-ca	america/vancouver	49.05798	-122.25257	255405
kelowna-02-ca	america/vancouver	49.88307	-119.48568	191623
nanaimo-02-ca	america/vancouver	49.16634	-123.93601	138327
winnipeg-03-ca	america/winnipeg	49.8844	-97.14704	632063
calgary-01-ca	america/edmonton	51.05011	-114.08529	1060980
edmonton-01-ca	america/edmonton	53.55014	-113.46871	858501
halifax-07-ca	america/halifax	44.64533	-63.57239	480454
sydney-07-ca	america/glace_bay	46.1351	-60.1831	125936
moncton-04-ca	america/moncton	46.11594	-64.80186	106032
st. john's-05-ca	america/st_johns	47.56494	-52.70931	140940
toronto-08-ca	america/toronto	43.70011	-79.4163	7985697
ottawa-08-ca	america/toronto	45.41117	-75.69812	832919
hamilton-08-ca	america/toronto	43.23341	-79.94964	941309
kitchener-08-ca	america/toronto	43.42537	-80.5112	570712
london-08-ca	america/toronto	42.98339	-81.23304	382875
windsor-08-ca	america/toronto	42.30008	-83.01654	308441
oshawa-08-ca	america/toronto	43.90012	-78.84957	247989
barrie-08-ca	america/toronto	44.40011	-79.66634	280530
greater sudbury-08-ca	america/toronto	46.49	-80.99001	157857
st. catharines-08-ca	america/toronto	43.16681	-79.24958	317096
kingston-08-ca	america/toronto	44.22976	-76.48098	129327
chatham kent-08-ca	america/toronto	42.40009	-82.1831	108589
belleville-08-ca	america/toronto	44.17876	-77.37053	117014
terrebonne-1014-ca	america/montreal	45.70004	-73.64732	257076
saint jerome-1015-ca	america/montreal	45.78036	-74.00365	247238
longueuil-1016-ca	america/montreal	45.53121	-73.51806	712977
levis-1012-ca	america/montreal	46.80326	-71.17793	155966
laval-1013-ca	america/montreal	45.56995	-73.692	376845
saskatoon-11-ca	america/regina	52.11679	-106.63452	198958
regina-11-ca	america/regina	50.45008	-104.6178	176183
quebec-10-ca	america/montreal	46.81228	-71.21454	545111
saint laurent-10-ca	america/montreal	45.50008	-73.66585	279304
gatineau-1007-ca	america/montreal	45.47723	-75.70164	242124
montreal-1006-ca	america/montreal	45.50884	-73.58781	3298674
sherbrooke-1005-ca	america/montreal	45.40008	-71.89908	144997
trois rivieres-1004-ca	america/montreal	46.35006	-72.54912	168854
saguenay-1002-ca	america/montreal	48.41675	-71.06573	228060
dolisie-07-cg	africa/brazzaville	-4.19834	12.66664	103894
brazzaville-12-cg	africa/brazzaville	-4.26613	15.28318	1284609
pointe noire-7280295-cg	africa/brazzaville	-4.77609	11.86352	659084
bimbo-17-cf	africa/bangui	4.25671	18.41583	129655
bangui-18-cf	africa/bangui	4.36122	18.55496	542393
mbandaka-02-cd	africa/kinshasa	0.04865	18.26034	184185
gemena-02-cd	africa/kinshasa	3.25651	19.77234	117639
kananga-03-cd	africa/lubumbashi	-5.89624	22.41659	485809
tshikapa-03-cd	africa/lubumbashi	-6.41621	20.79995	267462
mwene ditu-00-cd	africa/lubumbashi	-7.0	23.45	189177
gandajika-00-cd	africa/lubumbashi	-6.75	23.95	154425
ilebo-00-cd	africa/lubumbashi	-4.31667	20.58333	107093
bukavu-12-cd	africa/lubumbashi	-2.50833	28.86083	262423
uvira-12-cd	africa/lubumbashi	-3.40667	29.14583	170391
kinshasa-06-cd	africa/kinshasa	-4.32142	15.30807	8271132
mbuji mayi-04-cd	africa/lubumbashi	-6.13603	23.58979	874761
lubumbashi-05-cd	africa/lubumbashi	-11.66089	27.47938	1373770
likasi-05-cd	africa/lubumbashi	-10.98139	26.73333	459116
kolwezi-05-cd	africa/lubumbashi	-10.71484	25.46674	418000
kalemie-05-cd	africa/lubumbashi	-5.94749	29.19471	146974
matadi-08-cd	africa/kinshasa	-5.79949	13.44068	180109
kisangani-09-cd	africa/lubumbashi	0.51528	25.19099	539158
isiro-09-cd	africa/lubumbashi	2.77391	27.61603	127076
kikwit-01-cd	africa/kinshasa	-5.04098	18.81619	186991
bandundu-01-cd	africa/kinshasa	-3.31667	17.36667	118211
butembo-11-cd	africa/lubumbashi	0.14164	29.29117	244269
goma-11-cd	africa/lubumbashi	-1.67917	29.22278	161275
kindu-10-cd	africa/lubumbashi	-2.95	25.95	135698
havirov-00-cz	europe/prague	49.77984	18.43688	191854
karlovy vary-81-cz	europe/prague	50.23271	12.87117	127156
prague-52-cz	europe/prague	50.08804	14.42076	1300921
kladno-88-cz	europe/prague	50.14734	14.10285	187525
usti nad labem-89-cz	europe/prague	50.6607	14.03227	438889
ceske budejovice-79-cz	europe/prague	48.97447	14.47434	148639
zlin-90-cz	europe/prague	49.22665	17.66633	341887
hradec kralove-82-cz	europe/prague	50.20923	15.83277	180334
liberec-83-cz	europe/prague	50.76711	15.05619	181489
jihlava-80-cz	europe/prague	49.3961	15.59124	177808
ostrava-85-cz	europe/prague	49.83465	18.28204	584429
pardubice-86-cz	europe/prague	50.04075	15.77659	127522
plzen-87-cz	europe/prague	49.74747	13.37759	187282
olomouc-84-cz	europe/prague	49.59552	17.25175	244303
brno-78-cz	europe/prague	49.19522	16.60796	412208
nicosia-04-cy	asia/nicosia	35.16667	33.36667	200452
limassol-05-cy	asia/nicosia	34.675	33.03333	154000
paraiso-02-cr	america/costa_rica	9.83832	-83.86556	112242
san francisco-04-cr	america/costa_rica	9.99299	-84.12934	125539
san jose-08-cr	america/costa_rica	9.93333	-84.08333	820755
willemstad--cw	america/curacao	12.1084	-68.93354	125000
praia-14-cv	atlantic/cape_verde	14.93152	-23.51254	113364
havana-02-cu	america/havana	23.13302	-82.38304	3805598
guantanamo-10-cu	america/havana	20.14444	-75.20917	298554
las tunas-13-cu	america/havana	20.96167	-76.95111	300618
holguin-12-cu	america/havana	20.88722	-76.26306	406212
moa-12-cu	america/havana	20.65694	-74.94028	111134
santiago de cuba-15-cu	america/havana	20.02472	-75.82194	725984
ciego de avila-07-cu	america/havana	21.84	-78.76194	282004
santa clara-16-cu	america/havana	22.4	-79.96667	634616
matanzas-03-cu	america/havana	23.04111	-81.5775	372819
colon-03-cu	america/havana	22.71917	-80.90583	165573
cienfuegos-08-cu	america/havana	22.14611	-80.43556	309238
camaguey-05-cu	america/havana	21.38083	-77.91694	477992
pinar del rio-01-cu	america/havana	22.4175	-83.69806	326227
bayamo-09-cu	america/havana	20.37917	-76.64333	433015
san jose de las lajas-ma-cu	america/havana	22.96139	-82.15111	174173
guira de melena-ar-cu	america/havana	22.79056	-82.50528	295964
sancti spiritus-14-cu	america/havana	21.92972	-79.4425	291685
bayamon-021-pr	america/puerto_rico	18.39856	-66.15572	203499
ponce-113-pr	america/puerto_rico	18.01108	-66.61406	152634
san juan-127-pr	america/puerto_rico	18.46633	-66.10572	418140
carolina-031-pr	america/puerto_rico	18.38078	-65.95739	170404
kairouan-03-tn	africa/tunis	35.6781	10.09633	119794
qulaybiyah-00-tn	africa/tunis	36.84757	11.09386	113688
sousse-23-tn	africa/tunis	35.82539	10.63699	282547
midoun-28-tn	africa/tunis	33.80813	10.99228	261899
gabes-29-tn	africa/tunis	33.88146	10.0982	146533
mahdia-15-tn	africa/tunis	35.50472	11.06222	159850
monastir-16-tn	africa/tunis	35.77799	10.82617	249774
douane-19-tn	africa/tunis	36.44766	10.7557	170312
sfax-32-tn	africa/tunis	34.74056	10.76028	311022
gafsa-30-tn	africa/tunis	34.425	8.78417	123131
tunis-36-tn	africa/tunis	36.81897	10.16579	1093740
bizerte-18-tn	africa/tunis	37.27442	9.87391	229829
aveiro-02-pt	europe/lisbon	40.64427	-8.64554	128305
funchal-10-pt	atlantic/madeira	32.63333	-16.9	133056
leiria-13-pt	europe/lisbon	39.74362	-8.80705	118030
coimbra-07-pt	europe/lisbon	40.20564	-8.41955	106582
porto-17-pt	europe/lisbon	41.14961	-8.61099	863888
setubal-19-pt	europe/lisbon	38.5244	-8.8882	531388
monsanto-18-pt	europe/lisbon	39.46203	-8.7118	118440
faro-09-pt	europe/lisbon	37.01937	-7.93223	148810
braga-04-pt	europe/lisbon	41.55032	-8.42005	267201
lisbon-14-pt	europe/lisbon	38.71667	-9.13333	1611783
san lorenzo-06-py	america/asuncion	-25.33968	-57.50879	1139074
asuncion-22-py	america/asuncion	-25.30066	-57.63591	1482200
caaguazu-04-py	america/asuncion	-25.45	-56.01667	106094
dili-di-tl	asia/dili	-8.55861	125.57361	150000
david-02-pa	america/panama	8.42729	-82.43085	116054
colon-04-pa	america/panama	9.35917	-79.90139	106250
panama-08-pa	america/panama	8.9936	-79.51973	1248640
port moresby-20-pg	pacific/port_moresby	-9.44314	147.17972	283733
lima-lma-pe	america/lima	-12.04318	-77.02824	7737002
chimbote-02-pe	america/lima	-9.08528	-78.57833	332049
pucallpa-25-pe	america/lima	-8.37915	-74.55387	310750
piura-20-pe	america/lima	-5.2	-80.63333	682487
callao-07-pe	america/lima	-12.06667	-77.15	813264
arequipa-04-pe	america/lima	-16.39889	-71.535	841130
tacna-23-pe	america/lima	-18.00556	-70.24833	280098
cusco-08-pe	america/lima	-13.51833	-71.97806	312140
tumbes-24-pe	america/lima	-3.56694	-80.45153	126130
cajamarca-06-pe	america/lima	-7.16378	-78.50027	135000
juliaca-21-pe	america/lima	-15.5	-70.13333	362227
ica-11-pe	america/lima	-14.06528	-75.73083	246844
chincha alta-11-pe	america/lima	-13.40985	-76.13235	230760
huanuco-10-pe	america/lima	-9.9329	-76.24153	147959
trujillo-13-pe	america/lima	-8.11599	-79.02998	869848
chepen-13-pe	america/lima	-7.22884	-79.42599	112783
huancayo-12-pe	america/lima	-12.06667	-75.23333	397714
tarma-12-pe	america/lima	-11.41972	-75.69083	100015
surco-15-pe	america/lima	-12.15	-77.01667	408563
huacho-15-pe	america/lima	-11.10667	-77.605	148216
chiclayo-14-pe	america/lima	-6.77361	-79.84167	779511
iquitos-16-pe	america/lima	-3.74806	-73.24722	437620
cerro de pasco-19-pe	america/lima	-10.68333	-76.26667	107576
ayacucho-05-pe	america/lima	-13.15833	-74.22389	158660
quetta-02-pk	asia/karachi	30.199	67.00971	873285
peshawar-03-pk	asia/karachi	34.008	71.57849	2088231
mingaora-03-pk	asia/karachi	34.77584	72.36249	273410
abbottabad-03-pk	asia/karachi	34.14685	73.21449	323092
dera ismail khan-03-pk	asia/karachi	31.83269	70.9024	208725
swabi-03-pk	asia/karachi	34.11988	72.46987	183778
kotli-06-pk	asia/karachi	33.51667	73.91667	690000
bhimbar-06-pk	asia/karachi	32.97568	74.07926	342900
lahore-04-pk	asia/karachi	31.54972	74.34361	7565364
faisalabad-04-pk	asia/karachi	31.41667	73.08333	3379367
rawalpindi-04-pk	asia/karachi	33.6007	73.0679	1904052
multan-04-pk	asia/karachi	30.19556	71.47528	1803305
gujranwala-04-pk	asia/karachi	32.16167	74.18831	2389281
bahawalpur-04-pk	asia/karachi	29.4	71.68333	800301
sargodha-04-pk	asia/karachi	32.08361	72.67111	1027384
sialkot-04-pk	asia/karachi	32.5101	74.54313	689082
jhang sadr-04-pk	asia/karachi	31.27154	72.32842	410274
dera ghazi khan-04-pk	asia/karachi	30.05614	70.63477	299884
montgomery-04-pk	asia/karachi	30.66667	73.1	1180940
sadiqabad-04-pk	asia/karachi	28.30623	70.13065	212829
burewala-04-pk	asia/karachi	30.16667	72.65	495180
jhelum-04-pk	asia/karachi	32.93313	73.72637	524349
khanpur-04-pk	asia/karachi	28.64534	70.6567	176547
bahawalnagar-04-pk	asia/karachi	29.99866	73.2536	254195
ahmadpur east-04-pk	asia/karachi	29.14309	71.25976	150180
kot addu-04-pk	asia/karachi	30.4692	70.96714	149086
chakwal-04-pk	asia/karachi	32.93338	72.85853	231925
mianwali-04-pk	asia/karachi	32.5741	71.52639	198883
hasilpur-04-pk	asia/karachi	29.71222	72.55528	183543
bhai pheru-04-pk	asia/karachi	31.2	73.95	336557
attock city-04-pk	asia/karachi	33.77311	72.3741	111788
bhakkar-04-pk	asia/karachi	31.62525	71.06574	171314
dipalpur-04-pk	asia/karachi	30.67091	73.65292	264880
chuhar kana-04-pk	asia/karachi	31.75	73.8	148832
narowal-04-pk	asia/karachi	32.1	74.88333	160808
karachi-05-pk	asia/karachi	24.9056	67.0822	11924219
hyderabad-05-pk	asia/karachi	25.39242	68.37366	1779127
sukkur-05-pk	asia/karachi	27.70516	68.85738	917408
larkana-05-pk	asia/karachi	27.55508	68.21414	778332
nawabshah-05-pk	asia/karachi	26.24833	68.40955	383376
mirpur khas-05-pk	asia/karachi	25.5251	69.0159	434192
jacobabad-05-pk	asia/karachi	28.281	68.43876	205060
dadu-05-pk	asia/karachi	26.73286	67.77631	384173
kandhkot-05-pk	asia/karachi	28.24396	69.18235	287846
umarkot-05-pk	asia/karachi	25.36157	69.73624	105055
islamabad-08-pk	asia/karachi	33.72148	73.04329	601600
san fernando-0136-ph	asia/manila	16.61591	120.31663	129937
bayugan-1303-ph	asia/manila	8.75611	125.7675	103327
baguio-15a4-ph	asia/manila	16.41639	120.59306	272714
santiago-0231-ph	asia/manila	16.68808	121.5487	202304
dasmarinas-4020-ph	asia/manila	14.32944	120.93667	1743732
tagum-11i7-ph	asia/manila	7.44778	125.80778	564457
puerto princesa-00f1-ph	asia/manila	9.73917	118.73528	157144
san jose-4140-ph	asia/manila	12.35275	121.06761	118807
general santos-12c6-ph	asia/manila	6.11278	125.17167	679588
iloilo-0630-ph	asia/manila	10.69694	122.56444	430475
mariveles-0307-ph	asia/manila	14.4361	120.4857	501782
jolo-1460-ph	asia/manila	6.05222	121.00222	101002
panalanoy-00g1-ph	asia/manila	11.25111	125.00639	189090
laoag-0128-ph	asia/manila	18.1978	120.5957	122004
calamba-4033-ph	asia/manila	14.21167	121.16528	1634184
cebu city-0721-ph	asia/manila	10.31672	123.89071	1527143
lucena-40h2-ph	asia/manila	13.93139	121.61722	573351
catanauan-40h2-ph	asia/manila	13.5926	122.3215	112067
quezon city-ncrf2-ph	asia/manila	14.6488	121.0509	2761720
digos-1125-ph	asia/manila	6.74972	125.35722	211977
mati-1126-ph	asia/manila	6.95508	126.21655	153491
legaspi-05d5-ph	asia/manila	13.13722	123.73444	179481
catbalogan-0855-ph	asia/manila	11.77528	124.88611	136002
zamboanga-09-ph	asia/manila	6.91028	122.07389	457623
malingao-1257-ph	asia/manila	7.16083	124.475	1186675
roxas city-0618-ph	asia/manila	11.58528	122.75111	102688
cotabato-14b8-ph	asia/manila	7.22361	124.24639	179433
valencia-1012-ph	asia/manila	7.90639	125.09417	241767
iligan city-1234-ph	asia/manila	8.25	124.4	312323
angeles city-0350-ph	asia/manila	15.15	120.58333	1660530
marawi city-1435-ph	asia/manila	8.0034	124.28395	143627
taguig-4053-ph	asia/manila	14.5243	121.0792	2567403
iriga city-0516-ph	asia/manila	13.4324	123.4115	309095
daet-0515-ph	asia/manila	14.1122	122.9553	134474
dumaguete-0746-ph	asia/manila	9.307	123.3074	272822
tuguegarao city-0214-ph	asia/manila	17.61306	121.72694	186580
santol-00a1-ph	asia/manila	15.16222	120.5675	298976
libertad-00a8-ph	asia/manila	8.94417	125.50194	250353
manila-ncrd9-ph	asia/manila	14.6042	120.9822	10444527
pasig city-ncrl8-ph	asia/manila	14.58691	121.0614	617301
cabanatuan-0347-ph	asia/manila	15.4867	120.9676	946218
polangui-0505-ph	asia/manila	13.2923	123.4855	269539
bayombong-0248-ph	asia/manila	16.4812	121.1497	132219
muricay-0966-ph	asia/manila	7.8275	123.4782	170326
dipolog-0965-ph	asia/manila	8.5883	123.3409	144063
makati city-ncrk4-ph	asia/manila	14.55027	121.03269	510383
mandaluyong city-ncrk8-ph	asia/manila	14.5832	121.0409	305576
budta-1456-ph	asia/manila	7.20417	124.43972	1367091
mantampay-00c8-ph	asia/manila	8.16667	124.21667	280522
tanza-ncrb4-ph	asia/manila	14.6753	120.9389	105510
batangas-4009-ph	asia/manila	13.7567	121.0584	907778
tarlac-0363-ph	asia/manila	15.48945	120.59193	552975
subic-0364-ph	asia/manila	14.87999	120.23433	150817
masinloc-0364-ph	asia/manila	15.5363	119.9502	104399
mandaue city-00d8-ph	asia/manila	10.32361	123.92222	288892
davao-11c3-ph	asia/manila	7.07306	125.61278	1212504
tagbilaran city-0711-ph	asia/manila	9.65556	123.85219	104127
lapu lapu city-00d4-ph	asia/manila	10.31028	123.94944	241374
mansilingan-00a2-ph	asia/manila	10.63111	122.97889	454150
koronadal-1270-ph	asia/manila	6.50306	124.84694	237213
tacurong-1271-ph	asia/manila	6.6925	124.67639	104129
bacolod city-06h3-ph	asia/manila	10.66667	122.95	1280133
kabankalan-06h3-ph	asia/manila	9.9902	122.8142	235728
sagay-06h3-ph	asia/manila	10.94472	123.42417	141824
cagayan de oro-1043-ph	asia/manila	8.48222	124.64722	491928
ozamiz city-1042-ph	asia/manila	8.1481	123.8405	162082
sorsogon-0558-ph	asia/manila	12.97389	123.99333	131975
urdaneta-0151-ph	asia/manila	15.97611	120.57111	442258
olongapo-00e3-ph	asia/manila	14.82917	120.28278	220021
naga-00e2-ph	asia/manila	13.61917	123.18139	147097
marawi-00e1-ph	asia/manila	7.99861	124.29278	143568
san jose del monte-0313-ph	asia/manila	14.81389	121.04528	2277163
opole-79-pl	europe/warsaw	50.66667	17.95	383067
olsztyn-85-pl	europe/warsaw	53.77995	20.49416	247911
elblag-85-pl	europe/warsaw	54.1522	19.40884	145914
elk-85-pl	europe/warsaw	53.82824	22.36469	120896
gierloz-85-pl	europe/warsaw	54.08134	21.49551	104147
krakow-77-pl	europe/warsaw	50.08333	19.91667	999815
tarnow-77-pl	europe/warsaw	50.01381	20.98698	247650
gorzow wielkopolski-76-pl	europe/warsaw	52.73679	15.22878	161198
zielona gora-76-pl	europe/warsaw	51.93548	15.50643	263629
lublin-75-pl	europe/warsaw	51.25	22.56667	530245
chelm-75-pl	europe/warsaw	51.14312	23.4716	172214
lodz-74-pl	europe/warsaw	51.75	19.46667	1259592
bydgoszcz-73-pl	europe/warsaw	53.1235	18.00762	819278
wloclawek-73-pl	europe/warsaw	52.64817	19.0678	120339
grudziadz-73-pl	europe/warsaw	53.48411	18.75366	126827
wroclaw-72-pl	europe/warsaw	51.1	17.03333	827914
walbrzych-72-pl	europe/warsaw	50.77141	16.28432	539791
lubin-72-pl	europe/warsaw	51.40089	16.20149	208309
gdansk-82-pl	europe/warsaw	54.35205	18.64637	1051074
slupsk-82-pl	europe/warsaw	54.46405	17.02872	166743
katowice-83-pl	europe/warsaw	50.25842	19.02754	3092008
czestochowa-83-pl	europe/warsaw	50.79646	19.12409	272258
rzeszow-80-pl	europe/warsaw	50.04132	21.99901	404009
przemysl-80-pl	europe/warsaw	49.78498	22.76728	106697
stalowa wola-80-pl	europe/warsaw	50.58286	22.05334	132527
bialystok-81-pl	europe/warsaw	53.13333	23.15	353861
poznan-86-pl	europe/warsaw	52.40692	16.92993	861953
kalisz-86-pl	europe/warsaw	51.76109	18.09102	283726
konin-86-pl	europe/warsaw	52.22338	18.25121	104751
pila-86-pl	europe/warsaw	53.15145	16.73782	130617
leszno-86-pl	europe/warsaw	51.84034	16.57494	105716
szczecin-87-pl	europe/warsaw	53.42894	14.55302	573863
koszalin-87-pl	europe/warsaw	54.19438	16.17222	176092
kielce-84-pl	europe/warsaw	50.87033	20.62752	366390
ostrowiec swietokrzyski-84-pl	europe/warsaw	50.92936	21.38525	115213
warsaw-78-pl	europe/warsaw	52.22977	21.01178	3973973
radom-78-pl	europe/warsaw	51.40253	21.14714	265437
plock-78-pl	europe/warsaw	52.54682	19.70638	187533
rijeka-12-hr	europe/zagreb	45.34306	14.40917	141172
split-15-hr	europe/zagreb	43.50891	16.43915	192241
zagreb   centar-21-hr	europe/zagreb	45.81313	15.97753	1551377
pecs-02-hu	europe/budapest	46.08333	18.23333	202284
debrecen-10-hu	europe/budapest	47.53333	21.63333	327701
veszprem-23-hu	europe/budapest	47.09327	17.91149	165317
kecskemet-01-hu	europe/budapest	46.90618	19.69128	156658
szeged-06-hu	europe/budapest	46.253	20.14824	267998
miskolc-04-hu	europe/budapest	48.1	20.78333	278504
budapest-05-hu	europe/budapest	47.49801	19.03991	3381055
nyiregyhaza-18-hu	europe/budapest	47.95539	21.71671	153206
szekesfehervar-08-hu	europe/budapest	47.18995	18.41034	151684
gyor-09-hu	europe/budapest	47.68333	17.63512	158624
erd-16-hu	europe/budapest	47.39489	18.9136	380462
tatabanya-12-hu	europe/budapest	47.58494	18.39325	163111
zalaegerszeg-24-hu	europe/budapest	46.84	16.84389	134255
paradsasvar-11-hu	europe/budapest	47.9126	19.97709	188295
szolnok-20-hu	europe/budapest	47.18333	20.2	145247
bekescsaba-03-hu	europe/budapest	46.68333	21.1	183410
hong kong-00-hk	asia/hong_kong	22.28552	114.15769	9320999
la ceiba-01-hn	america/tegucigalpa	15.75971	-86.78221	130218
san pedro sula-06-hn	america/tegucigalpa	15.5	-88.03333	790165
comayagua-04-hn	america/tegucigalpa	14.45	-87.63333	101925
el progreso-18-hn	america/tegucigalpa	15.4	-87.8	100810
tegucigalpa-08-hn	america/tegucigalpa	14.0818	-87.20681	850848
kuito-02-ao	africa/luanda	-12.38333	16.93333	132479
luanda-20-ao	africa/luanda	-8.83682	13.23432	2776168
huambo-08-ao	africa/luanda	-12.77611	15.73917	247350
lubango-09-ao	africa/luanda	-14.91717	13.4925	102541
lobito-01-ao	africa/luanda	-12.34806	13.54556	376135
parakou-10-africa/porto	novo	9.33716	2.63031	163753
abomey calavi-00-africa/porto	novo	6.44852	2.35566	405849
bohicon-00-africa/porto	novo	7.17826	2.0667	163658
cotonou-14-africa/porto	novo	6.36536	2.41833	690584
porto novo-16-africa/porto	novo	6.49646	2.60359	234168
natitingou-08-africa/porto	novo	10.30416	1.37962	100725
djougou-13-africa/porto	novo	9.70853	1.66598	202810
kandi-07-africa/porto	novo	11.13417	2.93861	109701
podgorica-16-me	europe/podgorica	42.44111	19.26361	136473
tiraspol-58-md	europe/chisinau	46.84028	29.64333	172356
chisinau-57-md	europe/chisinau	47.00556	28.8575	635994
balti-60-md	europe/chisinau	47.76167	27.92889	125000
bender-62-md	europe/chisinau	46.83056	29.47111	110175
toliara-7670913-mg	indian/antananarivo	-23.35	43.66667	115319
antanifotsy-05-mg	indian/antananarivo	-19.65	47.31667	136650
mahajanga-7670849-mg	indian/antananarivo	-15.71667	46.31667	154657
fianarantsoa-7670905-mg	indian/antananarivo	-21.45267	47.08569	167227
antananarivo-7670856-mg	indian/antananarivo	-18.91368	47.53613	1391433
toamasina-7670857-mg	indian/antananarivo	-18.1492	49.40234	206373
montevideo-10-uy	america/montevideo	-34.83346	-56.16735	1270737
las piedras-02-uy	america/montevideo	-34.72639	-56.22	181144
buxoro-02-uz	asia/samarkand	39.77472	64.42861	410178
samarqand-10-uz	asia/samarkand	39.65417	66.95972	430201
kattaqo'rg'on-10-uz	asia/samarkand	39.89889	66.25611	122461
tashkent-13-uz	asia/tashkent	41.26465	69.21627	2004408
andijon-01-uz	asia/tashkent	40.78206	72.34424	417905
namangan-06-uz	asia/tashkent	40.9983	71.67257	787181
chirchiq-14-uz	asia/tashkent	41.46889	69.58222	310395
angren-14-uz	asia/tashkent	41.01667	70.14361	308580
yangiyul-14-uz	asia/tashkent	41.11202	69.0471	152742
qo`qon-03-uz	asia/tashkent	40.52861	70.9425	255336
farg`ona-03-uz	asia/tashkent	40.38421	71.78432	410148
qarshi-08-uz	asia/samarkand	38.86667	65.8	324957
shahrisabz-08-uz	asia/samarkand	39.05778	66.83417	118345
nukus-09-uz	asia/samarkand	42.45306	59.61028	280006
guliston-16-uz	asia/tashkent	40.48972	68.78417	112825
tirmiz-12-uz	asia/samarkand	37.22417	67.27833	140385
jizzax-15-uz	asia/samarkand	40.11583	67.84222	190550
urganch-05-uz	asia/samarkand	41.55	60.63333	294724
navoiy-07-uz	asia/samarkand	40.08444	65.37917	154752
taunggyi-11-mm	asia/rangoon	20.78333	97.03333	160115
lashio-11-mm	asia/rangoon	22.93333	97.75	131016
pathein-03-mm	asia/rangoon	16.78333	94.73333	237089
hinthada-03-mm	asia/rangoon	17.63333	95.46667	134947
bogale-03-mm	asia/rangoon	16.28333	95.4	268784
mawlamyine-13-mm	asia/rangoon	16.49139	97.62556	624713
thaton-13-mm	asia/rangoon	16.92056	97.37139	123727
sittwe-01-mm	asia/rangoon	20.15	92.9	177743
pakokku-15-mm	asia/rangoon	21.33333	95.1	126938
yenangyaung-15-mm	asia/rangoon	20.46667	94.88333	355719
thayetmyo-15-mm	asia/rangoon	19.31667	95.18333	156082
rangoon-17-mm	asia/rangoon	16.80528	96.15611	4744566
monywa-10-mm	asia/rangoon	22.11667	95.13333	182011
mandalay-08-mm	asia/rangoon	21.97473	96.08359	1375882
nay pyi taw-08-mm	asia/rangoon	19.745	96.12972	1022409
meiktila-08-mm	asia/rangoon	20.86667	95.86667	177442
myingyan-08-mm	asia/rangoon	21.46667	95.38333	141713
bago-16-mm	asia/rangoon	17.33667	96.47972	321435
pyay-16-mm	asia/rangoon	18.81667	95.21667	172279
taungoo-16-mm	asia/rangoon	18.93333	96.43333	106945
myeik-12-mm	asia/rangoon	12.43333	98.6	173298
dawei-12-mm	asia/rangoon	14.08333	98.2	136783
kayes ndi-03-ml	africa/bamako	14.46099	-11.43538	175870
bamako-01-ml	africa/bamako	12.65	-8.0	1297281
sikasso-06-ml	africa/bamako	11.31755	-5.66654	144786
mopti-04-ml	africa/bamako	14.4843	-4.18296	108456
segou-05-ml	africa/bamako	13.4317	-6.2157	146290
macau-02-mo	asia/macau	22.20056	113.54611	520400
ulaanbaatar-20-mn	asia/ulaanbaatar	47.90771	106.88324	844818
tulsa-ok143-us	america/chicago	36.15398	-95.99278	576385
concord-nc025-us	america/new_york	35.40875	-80.57951	121691
woodbury-mn163-us	america/chicago	44.92386	-92.95938	160528
boise-id001-us	america/boise	43.6135	-116.20345	256197
layton-ut011-us	america/denver	41.06022	-111.97105	261964
south bend-in141-us	america/indiana/indianapolis	41.68338	-86.25001	179885
bend-or017-us	america/los_angeles	44.05817	-121.31531	102854
north port-fl115-us	america/new_york	27.04422	-82.23593	130022
richmond-va760-us	america/new_york	37.55376	-77.46026	204214
indianapolis-in097-us	america/indiana/indianapolis	39.76838	-86.15804	875719
troy-mi125-us	america/detroit	42.60559	-83.14993	752706
las vegas-nv003-us	america/los_angeles	36.17497	-115.13722	1863532
columbia-mo019-us	america/chicago	38.95171	-92.33407	108500
los angeles-ca037-us	america/los_angeles	34.05223	-118.24368	9988954
lancaster-ca037-us	america/los_angeles	34.69804	-118.13674	325305
valencia-ca037-us	america/los_angeles	34.44361	-118.60953	167471
hanford-ca031-us	america/los_angeles	36.32745	-119.64568	103311
columbus-ga215-us	america/new_york	32.46098	-84.98771	189885
quincy-ma021-us	america/new_york	42.25288	-71.00227	487451
brockton-ma023-us	america/new_york	42.08343	-71.01838	144683
boston-ma025-us	america/new_york	42.35843	-71.05977	1330893
worcester-ma027-us	america/new_york	42.26259	-71.80229	410651
centennial-co005-us	america/denver	39.57916	-104.87692	239908
aurora-co001-us	america/denver	39.72943	-104.83192	683305
davenport-ia163-us	america/chicago	41.52364	-90.57764	132902
germantown-md031-us	america/new_york	39.17316	-77.27165	721393
bowie-md033-us	america/new_york	38.94278	-76.73028	490810
clarksville-tn125-us	america/chicago	36.52977	-87.35945	132929
la crosse-wi063-us	america/chicago	43.80136	-91.23958	119526
charlotte-nc119-us	america/new_york	35.22709	-80.84313	852983
camden-nj007-us	america/new_york	39.92595	-75.11962	256620
hackensack-nj003-us	america/new_york	40.88593	-74.04347	501798
kennewick-wa005-us	america/los_angeles	46.21125	-119.13723	121975
ogden-ut057-us	america/denver	41.223	-111.97383	153598
waukegan-il097-us	america/chicago	42.36363	-87.84479	408267
deltona-fl127-us	america/new_york	28.90054	-81.26367	329937
pearland-tx039-us	america/chicago	29.56357	-95.28605	134350
salem-or047-us	america/los_angeles	44.9429	-123.0351	251078
youngstown-oh099-us	america/new_york	41.09978	-80.64952	132035
lorain-oh093-us	america/new_york	41.45282	-82.18237	207593
odessa-tx135-us	america/chicago	31.84568	-102.36764	122647
honolulu-hi003-us	pacific/honolulu	21.30694	-157.85833	648944
huntsville-al089-us	america/chicago	34.73037	-86.5861	223043
memphis-tn157-us	america/chicago	35.14953	-90.04898	1425919
cincinnati-oh061-us	america/new_york	39.162	-84.45689	354037
naperville-il043-us	america/chicago	41.78586	-88.14729	737221
lansing-mi065-us	america/detroit	42.73254	-84.55553	227438
college station-tx041-us	america/chicago	30.62798	-96.33441	170058
montgomery-al101-us	america/chicago	32.36681	-86.29997	205764
fayetteville-ar143-us	america/chicago	36.06258	-94.15743	143377
ann arbor-mi161-us	america/detroit	42.27756	-83.74088	133369
sanford-fl117-us	america/new_york	28.80055	-81.27312	233345
detroit-mi163-us	america/detroit	42.33143	-83.04575	1524970
port saint lucie-fl111-us	america/new_york	27.29393	-80.35033	206193
kansas city-ks209-us	america/chicago	39.11417	-94.62746	145786
saint paul-mn123-us	america/chicago	44.94441	-93.09327	427042
durham-nc063-us	america/new_york	35.99403	-78.89862	228330
winston salem-nc067-us	america/new_york	36.09986	-80.24422	271367
carmel-in057-us	america/indiana/indianapolis	39.97837	-86.11804	238022
pittsburgh-pa003-us	america/new_york	40.44062	-79.99589	587391
lakewood-co059-us	america/denver	39.70471	-105.08137	355164
rio rancho-nm043-us	america/denver	35.23338	-106.66447	175042
minneapolis-mn053-us	america/chicago	44.97997	-93.26384	1243807
san luis obispo-ca079-us	america/los_angeles	35.28275	-120.65962	134552
san bernardino-ca071-us	america/los_angeles	34.10834	-117.28977	1645230
san diego-ca073-us	america/los_angeles	32.71533	-117.15726	2447535
oceanside-ca073-us	america/los_angeles	33.19587	-117.37948	396782
san francisco-ca075-us	america/los_angeles	37.77493	-122.41942	805235
stockton-ca077-us	america/los_angeles	37.9577	-121.29078	521882
buffalo-ny029-us	america/new_york	42.88645	-78.87837	640725
savannah-ga051-us	america/new_york	32.08354	-81.09983	170564
fargo-nd017-us	america/chicago	46.87719	-96.7898	131379
crystal lake-il111-us	america/chicago	42.24113	-88.3162	194078
lafayette-la055-us	america/chicago	30.22409	-92.01984	120623
metairie terrace-la051-us	america/chicago	29.97854	-90.16396	458593
florissant-mo189-us	america/chicago	38.78922	-90.32261	531321
madison-wi025-us	america/chicago	43.07305	-89.40123	305275
o'fallon-mo183-us	america/chicago	38.81061	-90.69985	226768
granite city-il119-us	america/chicago	38.70144	-90.14872	154819
chico-ca007-us	america/los_angeles	39.72849	-121.83748	127951
anchorage-ak020-us	america/anchorage	61.21806	-149.90028	291826
oakland-ca001-us	america/los_angeles	37.80437	-122.2708	1524539
sioux falls-sd099-us	america/chicago	43.54997	-96.70033	153888
overland park-ks091-us	america/chicago	38.98223	-94.67079	482080
beavercreek-oh057-us	america/new_york	39.70923	-84.06327	103264
tallahassee-fl073-us	america/new_york	30.43826	-84.28073	181376
southaven-ms033-us	america/chicago	34.98898	-90.01259	108532
waterloo-ia013-us	america/chicago	42.49276	-92.34296	107666
baltimore-md510-us	america/new_york	39.29038	-76.61219	620961
cape coral-fl071-us	america/new_york	26.56285	-81.94953	441513
des moines-ia153-us	america/chicago	41.60054	-93.60911	377812
billings-mt111-us	america/denver	45.78329	-108.50069	104170
santa rosa-ca097-us	america/los_angeles	38.44047	-122.71443	293528
vallejo-ca095-us	america/los_angeles	38.10409	-122.25664	368799
tacoma-wa053-us	america/los_angeles	47.25288	-122.44429	499771
chesapeake-va550-us	america/new_york	36.81904	-76.27494	222209
wilmington-nc129-us	america/new_york	34.22573	-77.94471	106476
modesto-ca099-us	america/los_angeles	37.6391	-120.99688	378897
hammond-in089-us	america/chicago	41.58337	-87.50004	392300
fayetteville-nc051-us	america/new_york	35.05266	-78.87836	244923
league city-tx167-us	america/chicago	29.50745	-95.09493	230887
virginia beach-va810-us	america/new_york	36.85293	-75.97798	437994
greenville-sc045-us	america/new_york	34.85262	-82.39401	167290
west gulfport-ms047-us	america/chicago	30.40409	-89.0942	183176
chester-pa045-us	america/new_york	39.84956	-75.35575	147148
erie-pa049-us	america/new_york	42.12922	-80.08506	101786
jackson-ms049-us	america/chicago	32.29876	-90.18481	198730
lake oswego-or005-us	america/los_angeles	45.42067	-122.67065	165845
dayton-oh113-us	america/new_york	39.75895	-84.19161	344849
albuquerque-nm001-us	america/denver	35.08449	-106.65114	586828
east pensacola heights-fl033-us	america/chicago	30.42881	-87.17997	264411
jacksonville-fl031-us	america/new_york	30.33218	-81.65565	843146
syracuse-ny067-us	america/new_york	43.04812	-76.14742	145170
wichita falls-tx485-us	america/chicago	33.91371	-98.49339	104553
greeley-co123-us	america/denver	40.42331	-104.70913	130070
coon rapids-mn003-us	america/chicago	45.11997	-93.28773	272286
lawrenceville-ga135-us	america/new_york	33.95621	-83.98796	107265
fort collins-co069-us	america/denver	40.58526	-105.08442	210845
san rafael-ca041-us	america/los_angeles	37.97353	-122.53109	109617
merced-ca047-us	america/los_angeles	37.30216	-120.48297	143098
racine-wi101-us	america/chicago	42.72613	-87.78285	103565
janesville-wi105-us	america/chicago	42.68279	-89.01872	100541
miami-fl086-us	america/new_york	25.77427	-80.19366	2227611
portland-me005-us	america/new_york	43.66147	-70.25533	175464
yonkers-ny119-us	america/new_york	40.93121	-73.89875	640844
wichita-ks173-us	america/chicago	37.69224	-97.33754	404526
boulder-co013-us	america/denver	40.01499	-105.27055	244619
topeka-ks177-us	america/chicago	39.04833	-95.67804	127473
cedar rapids-ia113-us	america/chicago	42.00833	-91.64407	161094
knoxville-tn093-us	america/new_york	35.96064	-83.92074	199550
columbia-md027-us	america/new_york	39.24038	-76.83942	271340
south bel air-md025-us	america/new_york	39.53316	-76.33746	186592
milwaukee-wi079-us	america/chicago	43.0389	-87.90647	847685
lubbock-tx303-us	america/chicago	33.57786	-101.85517	229573
jersey city-nj017-us	america/new_york	40.72816	-74.07764	597221
newark-nj013-us	america/new_york	40.73566	-74.17237	708748
shreveport-la017-us	america/chicago	32.52515	-93.75018	199311
vineland-nj011-us	america/new_york	39.48623	-75.02573	172595
alexandria-va510-us	america/new_york	38.80484	-77.04692	139966
waco-tx309-us	america/chicago	31.54933	-97.14667	124805
eugene-or039-us	america/los_angeles	44.05207	-123.08675	215588
provo-ut049-us	america/denver	40.23384	-111.65853	445165
fort worth-tx439-us	america/chicago	32.72541	-97.32085	1620353
peoria-il143-us	america/chicago	40.69365	-89.58899	228011
ironville-ky019-us	america/new_york	38.45647	-82.69238	598982
denton-tx121-us	america/chicago	33.21484	-97.13307	370559
ashburn-va107-us	america/new_york	39.04372	-77.48749	138205
mentor-oh085-us	america/new_york	41.66616	-81.33955	107567
vancouver-wa011-us	america/los_angeles	45.63873	-122.66149	275553
chicago-il031-us	america/chicago	41.85003	-87.65005	4584607
hamilton-oh017-us	america/new_york	39.3995	-84.56134	175052
kalamazoo-mi077-us	america/detroit	42.29171	-85.58723	120554
columbia-sc079-us	america/new_york	34.00071	-81.03481	149765
chattanooga-tn065-us	america/new_york	35.04563	-85.30968	357791
murfreesboro-tn149-us	america/chicago	35.84562	-86.39027	181317
salt lake city-ut035-us	america/denver	40.76078	-111.89105	1149114
evansville-in163-us	america/chicago	37.97476	-87.55585	117429
lakeland-fl105-us	america/new_york	28.03947	-81.9498	169129
wilmington-de003-us	america/new_york	39.74595	-75.54659	140547
wesley chapel-fl101-us	america/new_york	28.23973	-82.32787	140947
nampa-id027-us	america/boise	43.54072	-116.56346	127794
joliet-il197-us	america/chicago	41.52503	-88.08173	465056
newport news-va700-us	america/new_york	36.97876	-76.428	180719
visalia-ca107-us	america/los_angeles	36.33023	-119.29206	259338
philadelphia-pa101-us	america/new_york	39.95234	-75.16379	1526006
atlanta-ga121-us	america/new_york	33.749	-84.38798	822310
amarillo-tx375-us	america/chicago	35.222	-101.8313	190695
waukesha-wi133-us	america/chicago	43.01168	-88.23148	223742
brentwood-ny103-us	america/new_york	40.78121	-73.24623	893372
oshkosh-wi139-us	america/chicago	44.02471	-88.54261	108937
fresno-ca019-us	america/los_angeles	36.74773	-119.77237	661979
concord-ca013-us	america/los_angeles	37.97798	-122.03107	921226
staten island-ny085-us	america/new_york	40.56233	-74.13986	468730
new city-ny087-us	america/new_york	41.1476	-73.98931	117076
jamaica-ny081-us	america/new_york	40.69149	-73.80569	242461
laredo-tx479-us	america/chicago	27.50641	-99.50754	236091
raleigh-nc183-us	america/new_york	35.7721	-78.63861	1032397
omaha-ne055-us	america/chicago	41.25861	-95.93779	408958
columbus-oh049-us	america/new_york	39.96118	-82.99879	1049888
athens-ga059-us	america/new_york	33.96095	-83.37794	116714
louisville-ky111-us	america/kentucky/louisville	38.25424	-85.75941	422216
spokane-wa063-us	america/los_angeles	47.65966	-117.42908	324548
everett-wa061-us	america/los_angeles	47.97898	-122.20208	444111
olympia-wa067-us	america/los_angeles	47.03787	-122.9007	106242
hillsboro-or067-us	america/los_angeles	45.52289	-122.98983	364851
rockford-il201-us	america/chicago	42.27113	-89.094	200366
sugar land-tx157-us	america/chicago	29.61968	-95.63495	299479
little rock-ar119-us	america/chicago	34.74648	-92.28959	330878
suffolk-va800-us	america/new_york	36.72821	-76.58356	165275
fort wayne-in003-us	america/indiana/indianapolis	41.1306	-85.12886	253691
allentown-pa077-us	america/new_york	40.60843	-75.49018	142928
nashville-tn037-us	america/chicago	36.16589	-86.78444	546773
plano-tx085-us	america/chicago	33.01984	-96.69889	651328
grand rapids-mi081-us	america/detroit	42.96336	-85.66809	373654
bethlehem-pa095-us	america/new_york	40.62593	-75.37046	101782
norristown-pa091-us	america/new_york	40.1215	-75.3399	126706
palm bay-fl009-us	america/new_york	28.03446	-80.58866	239679
canton-oh151-us	america/new_york	40.79895	-81.37845	144966
rochester-ny055-us	america/new_york	43.15478	-77.61556	298866
gainesville-fl001-us	america/new_york	29.65163	-82.32483	124354
portsmouth heights-va740-us	america/new_york	36.82098	-76.36883	194584
akron-oh153-us	america/new_york	41.08144	-81.51901	394442
round rock-tx491-us	america/chicago	30.50826	-97.6789	275851
eagan-mn037-us	america/chicago	44.80413	-93.16689	368262
hempstead-ny059-us	america/new_york	40.70621	-73.61874	899368
salinas-ca053-us	america/los_angeles	36.67774	-121.6555	289333
new bedford-ma005-us	america/new_york	41.63622	-70.9342	377806
anaheim-ca059-us	america/los_angeles	33.83529	-117.9145	2856186
lynn-ma009-us	america/new_york	42.46676	-70.94949	663260
orlando-fl095-us	america/new_york	28.53834	-81.37924	611345
kissimmee-fl097-us	america/new_york	28.30468	-81.41667	174137
davis-ca113-us	america/los_angeles	38.54491	-121.74052	169834
west palm beach-fl099-us	america/new_york	26.71534	-80.05337	689438
oxnard-ca111-us	america/los_angeles	34.1975	-119.17705	898491
norman-ok027-us	america/chicago	35.22257	-97.43948	166006
houston-tx201-us	america/chicago	29.76328	-95.36327	2678344
green bay-wi009-us	america/chicago	44.51916	-88.01983	162219
waldorf-md017-us	america/new_york	38.62456	-76.93914	104128
dunwoody-ga089-us	america/new_york	33.94621	-84.33465	240476
edison-nj023-us	america/new_york	40.51872	-74.4121	595852
trenton-nj021-us	america/new_york	40.21705	-74.74294	121472
parsippany-nj027-us	america/new_york	40.85788	-74.42599	103557
the woodlands-tx339-us	america/chicago	30.15799	-95.48938	150054
toms river-nj029-us	america/new_york	39.95373	-74.19792	177130
abilene-tx441-us	america/chicago	32.44874	-99.73314	117063
medford-or029-us	america/los_angeles	42.32652	-122.87559	112154
dallas-tx113-us	america/chicago	32.78306	-96.80667	2534081
flint-mi049-us	america/detroit	43.01253	-83.68746	132433
norwich-ct011-us	america/new_york	41.52426	-72.07591	103505
yuma-az027-us	america/phoenix	32.72532	-114.6244	144834
san tan valley-az021-us	america/phoenix	33.1911	-111.528	207899
tuscaloosa-al125-us	america/chicago	33.20984	-87.56917	113798
tuckahoe-va087-us	america/new_york	37.59015	-77.55638	102143
brownsville-tx061-us	america/chicago	25.90175	-97.49748	264122
saint petersburg-fl103-us	america/new_york	27.77086	-82.67927	702307
derry village-nh015-us	america/new_york	42.89175	-71.31201	106882
manchester-nh011-us	america/new_york	42.99564	-71.45479	243973
rochester-mn109-us	america/chicago	44.02163	-92.4699	106769
greensboro-nc081-us	america/new_york	36.07264	-79.79198	374037
denver-co031-us	america/denver	39.73915	-104.9847	600158
highlands ranch-co035-us	america/denver	39.55388	-104.96943	190241
borough of bronx-ny005-us	america/new_york	40.84985	-73.86641	1404662
tampa-fl057-us	america/new_york	27.94752	-82.45843	1101426
norfolk-va710-us	america/new_york	36.84681	-76.28522	242803
albany-ny001-us	america/new_york	42.65258	-73.75623	207818
new york city-ny-us	america/new_york	40.71427	-74.00597	8175133
east hampton-va650-us	america/new_york	37.03737	-76.33161	285429
pueblo-co101-us	america/denver	38.25445	-104.60914	136232
new orleans-la071-us	america/chicago	29.95465	-90.07507	343829
saint louis-mo510-us	america/chicago	38.62727	-90.19789	319294
franklin-tn187-us	america/chicago	35.92506	-86.86889	130826
dale city-va153-us	america/new_york	38.63706	-77.31109	210818
bakersfield-ca029-us	america/los_angeles	35.37329	-119.01871	510165
el centro-ca025-us	america/los_angeles	32.792	-115.56305	106123
lincoln-ne109-us	america/chicago	40.8	-96.66696	258379
arlington-va013-us	america/new_york	38.88101	-77.10428	207627
springfield-mo077-us	america/chicago	37.21533	-93.29824	159498
marietta-ga067-us	america/new_york	33.9526	-84.54993	195173
lexington fayette-ky067-us	america/new_york	38.0498	-84.45855	521169
kansas city-mo095-us	america/chicago	39.09973	-94.57857	885232
kenosha-wi059-us	america/chicago	42.58474	-87.82119	118937
toledo-oh095-us	america/new_york	41.66394	-83.55521	326464
beaumont-tx245-us	america/chicago	30.08605	-94.10185	205805
yakima-wa077-us	america/los_angeles	46.60207	-120.5059	106925
killeen-tx027-us	america/chicago	31.11712	-97.7278	268528
portland-or051-us	america/los_angeles	45.52345	-122.67621	725488
san antonio-tx029-us	america/chicago	29.42412	-98.49363	1364135
el paso-tx141-us	america/denver	31.75872	-106.48693	726506
bloomington-il113-us	america/chicago	40.4842	-88.99369	129107
phoenix-az013-us	america/phoenix	33.44838	-112.07404	3721794
mobile-al097-us	america/chicago	30.69436	-88.04305	235168
warren-mi099-us	america/detroit	42.47754	-83.0277	593377
tucson-az019-us	america/phoenix	32.22174	-110.92648	821398
charleston-sc019-us	america/new_york	32.77657	-79.93092	285397
washington, d. c.-dc001-us	america/new_york	38.89511	-77.03637	601723
birmingham-al073-us	america/chicago	33.52066	-86.80249	453884
oklahoma city-ok109-us	america/chicago	35.46756	-97.51643	756158
fort lauderdale-fl011-us	america/new_york	26.12231	-80.14338	1673505
brooklyn-ny047-us	america/new_york	40.6501	-73.94958	2593862
colorado springs-co041-us	america/denver	38.83388	-104.82136	491316
reno-nv031-us	america/los_angeles	39.52963	-119.8138	349848
springfield-ma013-us	america/new_york	42.10148	-72.58981	472532
lowell-ma017-us	america/new_york	42.63342	-71.31617	1354732
sacramento-ca067-us	america/los_angeles	38.58157	-121.4944	1360592
riverside-ca065-us	america/los_angeles	33.95335	-117.39616	1331293
temecula-ca065-us	america/los_angeles	33.49364	-117.14836	100097
indio-ca065-us	america/los_angeles	33.72058	-116.21556	341560
roseville-ca061-us	america/los_angeles	38.75212	-121.28801	238983
centreville-va059-us	america/new_york	38.84039	-77.42888	711057
niagara falls-ny063-us	america/new_york	43.0945	-79.05671	102926
manhattan-ny061-us	america/new_york	40.78343	-73.96625	1487536
lynchburg-va680-us	america/new_york	37.41375	-79.14225	141085
dundalk-md005-us	america/new_york	39.25066	-76.52052	625579
glen burnie-md003-us	america/new_york	39.16261	-76.62469	416993
corpus christi-tx355-us	america/chicago	27.80058	-97.39638	305215
seattle-wa033-us	america/los_angeles	47.60621	-122.33207	1694484
midland-tx329-us	america/chicago	31.99735	-102.07791	111147
warwick-ri003-us	america/new_york	41.7001	-71.41617	148343
elizabeth-nj039-us	america/new_york	40.66399	-74.2107	440617
providence-ri007-us	america/new_york	41.82399	-71.41283	527726
bridgewater-nj035-us	america/new_york	40.60079	-74.64815	103794
baton rouge-la033-us	america/chicago	30.45075	-91.15455	274756
paterson-nj031-us	america/new_york	40.91677	-74.17181	403790
austin-tx453-us	america/chicago	30.26715	-97.74306	837326
santa maria-ca083-us	america/los_angeles	34.95303	-120.43572	170892
santa barbara-ca083-us	america/los_angeles	34.42083	-119.69819	141394
belleville-il163-us	america/chicago	38.52005	-89.98399	132084
aurora-il089-us	america/chicago	41.76058	-88.32007	504035
moline-il161-us	america/chicago	41.5067	-90.51513	103803
springfield-il167-us	america/chicago	39.80172	-89.64371	116250
rogers-ar007-us	america/chicago	36.33202	-94.11854	154201
san jose-ca085-us	america/los_angeles	37.33939	-121.89496	1695955
mcallen-tx215-us	america/chicago	26.20341	-98.23001	473682
santa cruz-ca087-us	america/los_angeles	36.97412	-122.0308	128303
new haven-ct009-us	america/new_york	41.30815	-72.92816	763081
daly city-ca081-us	america/los_angeles	37.70577	-122.46192	612452
champaign-il019-us	america/chicago	40.11642	-88.24338	122305
hartford-ct003-us	america/new_york	41.76371	-72.68509	633391
cleveland-oh035-us	america/new_york	41.4995	-81.69541	1076364
bridgeport-ct001-us	america/new_york	41.16704	-73.20483	890326
vacoas-17-mu	indian/mauritius	-20.29806	57.47833	275161
port louis-18-mu	indian/mauritius	-20.16194	57.49889	155226
blantyre-s24-mw	africa/blantyre	-15.78499	35.00854	584877
lilongwe-c11-mw	africa/blantyre	-13.96692	33.78725	646750
male-40-mv	indian/maldives	4.1748	73.50888	103693
fort de france-mq972-mq	america/martinique	14.60892	-61.07334	242508
nouakchott-nkc-mr	africa/nouakchott	18.08581	-15.9785	661400
mbarara-w52-ug	africa/kampala	-0.60467	30.64851	176657
gulu-n30-ug	africa/kampala	2.77457	32.29899	146858
jinja-e33-ug	africa/kampala	0.43902	33.20317	108191
kampala-c37-ug	africa/kampala	0.31628	32.58219	1353189
entebbe-c96-ug	africa/kampala	0.06444	32.44694	101446
lira-n47-ug	africa/kampala	2.2499	32.89985	119323
kuching-11-my	asia/kuching	1.55	110.33333	570407
miri-11-my	asia/kuching	4.4148	114.0089	228212
sibu-11-my	asia/kuching	2.3	111.81667	227520
bintulu-11-my	asia/kuching	3.16667	113.03333	151617
kota bharu-03-my	asia/kuala_lumpur	6.13328	102.2386	409874
kuala terengganu-13-my	asia/kuala_lumpur	5.3302	103.1408	306475
cukai-13-my	asia/kuala_lumpur	4.25	103.41667	127870
johor bahru-01-my	asia/kuala_lumpur	1.4655	103.7578	1447020
kluang-01-my	asia/kuala_lumpur	2.0251	103.3328	388171
muar-01-my	asia/kuala_lumpur	2.0442	102.5689	193286
kuantan-06-my	asia/kuala_lumpur	3.8077	103.326	398055
temerluh-06-my	asia/kuala_lumpur	3.4506	102.4176	102087
kuala lumpur-14-my	asia/kuala_lumpur	3.1412	101.68653	1453975
melaka-04-my	asia/kuala_lumpur	2.196	102.2405	445994
kota kinabalu-16-my	asia/kuching	5.9749	116.0724	642245
sandakan-16-my	asia/kuching	5.8402	118.1179	392288
tawau-16-my	asia/kuching	4.2498	117.8871	306462
lahad datu-16-my	asia/kuching	5.0268	118.327	105622
sungai petani-02-my	asia/kuala_lumpur	5.647	100.48772	463281
alor setar-02-my	asia/kuala_lumpur	6.12104	100.36014	300088
seremban-05-my	asia/kuala_lumpur	2.7297	101.9381	546583
banting-00-my	asia/kuala_lumpur	2.81667	101.5	203430
klang-12-my	asia/kuala_lumpur	3.03333	101.45	3092871
george town-09-my	asia/kuala_lumpur	5.41123	100.33543	1070321
ipoh-07-my	asia/kuala_lumpur	4.5841	101.0829	1023398
teluk intan-07-my	asia/kuala_lumpur	4.0259	101.0213	132964
simpang empat-07-my	asia/kuala_lumpur	4.95	100.63333	105793
campeche-04-mx	america/merida	19.85	-90.53333	205212
ciudad del carmen-04-mx	america/merida	18.64973	-91.82471	141308
tijuana-02-mx	america/tijuana	32.5027	-117.00371	1500777
mexicali-02-mx	america/tijuana	32.65194	-115.46833	597099
ensenada-02-mx	america/tijuana	31.86612	-116.59972	274426
culiacan-25-mx	america/mazatlan	24.79944	-107.38972	653573
mazatlan-25-mx	america/mazatlan	23.2329	-106.40616	354717
los mochis-25-mx	america/mazatlan	25.79116	-108.99463	268517
guasave-25-mx	america/mazatlan	25.56648	-108.46907	127725
hermosillo-26-mx	america/hermosillo	29.06667	-110.96667	595811
ciudad obregon-26-mx	america/hermosillo	27.49221	-109.9395	258162
heroica nogales-26-mx	america/hermosillo	31.30862	-110.94217	185882
san luis rio colorado-26-mx	america/hermosillo	32.45612	-114.77186	139254
guaymas-26-mx	america/hermosillo	27.91818	-110.89973	142048
aguascalientes-01-mx	america/mexico_city	21.88333	-102.3	702525
ciudad juarez-06-mx	america/ojinaga	31.73333	-106.48333	1512354
chihuahua-06-mx	america/chihuahua	28.63333	-106.08333	708267
ciudad delicias-06-mx	america/chihuahua	28.19013	-105.47012	155202
hidalgo del parral-06-mx	america/chihuahua	26.92961	-105.6662	101768
saltillo-07-mx	america/monterrey	25.41667	-101.0	659508
torreon-07-mx	america/monterrey	25.54333	-103.4176	669255
monclova-07-mx	america/monterrey	26.90702	-101.42052	300371
ciudad acuna-07-mx	america/matamoros	29.32322	-100.95217	144669
piedras negras-07-mx	america/matamoros	28.72336	-100.56696	158258
sabinas-07-mx	america/monterrey	27.85591	-101.11738	135544
santiago de queretaro-22-mx	america/mexico_city	20.6	-100.38333	794250
cancun-23-mx	america/cancun	21.17429	-86.84656	542043
chetumal-23-mx	america/cancun	18.5	-88.3	134412
playa del carmen-23-mx	america/cancun	20.6274	-87.07987	174317
colima-08-mx	america/mexico_city	19.23333	-103.71667	318815
manzanillo-08-mx	america/mexico_city	19.05011	-104.31879	110735
mexico city-09-mx	america/mexico_city	19.42847	-99.12766	21375109
gustavo a. madero-28-mx	america/monterrey	22.83333	-98.76667	1265753
reynosa-28-mx	america/matamoros	26.07681	-98.29748	584135
heroica matamoros-28-mx	america/matamoros	25.88333	-97.5	482976
nuevo laredo-28-mx	america/matamoros	27.47629	-99.51639	349550
tampico-28-mx	america/monterrey	22.21667	-97.85	624382
ciudad victoria-28-mx	america/monterrey	23.73333	-99.13333	269923
tlaxcala-29-mx	america/mexico_city	19.31389	-98.24167	400854
tuxtla gutierrez-05-mx	america/mexico_city	16.75	-93.11667	565858
tapachula-05-mx	america/mexico_city	14.90696	-92.26185	227218
san cristobal de las casas-05-mx	america/mexico_city	16.73788	-92.63819	144070
las margaritas-05-mx	america/mexico_city	16.3119	-91.98028	183347
san luis potosi-24-mx	america/mexico_city	22.15	-100.98333	871710
ciudad valles-24-mx	america/mexico_city	21.98333	-99.01667	109504
la paz-03-mx	america/mazatlan	24.16667	-110.3	171485
villahermosa-27-mx	america/mexico_city	17.98333	-92.91667	605207
oaxaca de juarez-20-mx	america/mexico_city	17.05	-96.71667	340085
salina cruz-20-mx	america/mexico_city	16.18798	-95.19952	201824
puebla de zaragoza-21-mx	america/mexico_city	19.05	-98.2	2165594
tehuacan-21-mx	america/mexico_city	18.46148	-97.39282	282234
huauchinango-21-mx	america/mexico_city	20.18333	-98.05	135121
leon-11-mx	america/mexico_city	21.12131	-101.66801	1359726
irapuato-11-mx	america/mexico_city	20.6784	-101.34654	734487
celaya-11-mx	america/mexico_city	20.52353	-100.81566	497472
san luis de la paz-11-mx	america/mexico_city	21.3	-100.51667	172988
acambaro-11-mx	america/mexico_city	20.03024	-100.72249	106008
durango-10-mx	america/monterrey	24.03333	-104.66667	457140
gomez palacio-10-mx	america/monterrey	25.56473	-103.4958	292107
pachuca de soto-13-mx	america/mexico_city	20.11697	-98.73329	548807
tepeji de ocampo-13-mx	america/mexico_city	19.90528	-99.34389	125542
acapulco de juarez-12-mx	america/mexico_city	16.86336	-99.8901	652136
chilpancingo de los bravos-12-mx	america/mexico_city	17.55	-99.5	231188
iguala de la independencia-12-mx	america/mexico_city	18.34928	-99.53936	202805
ecatepec-15-mx	america/mexico_city	19.60111	-99.0525	9104948
toluca-15-mx	america/mexico_city	19.28833	-99.66722	1046349
guadalajara-14-mx	america/mexico_city	20.66667	-103.33333	3741527
puerto vallarta-14-mx	america/mexico_city	20.62041	-105.23066	205851
ciudad guzman-14-mx	america/mexico_city	19.70466	-103.4617	199380
lagos de moreno-14-mx	america/mexico_city	21.3559	-101.93399	152209
tepatitlan de morelos-14-mx	america/mexico_city	20.81692	-102.76347	198657
ocotlan-14-mx	america/mexico_city	20.3553	-102.77358	132286
cuernavaca-17-mx	america/mexico_city	18.94201	-99.22646	960764
morelia-16-mx	america/mexico_city	19.70078	-101.18443	641813
uruapan del progreso-16-mx	america/mexico_city	19.41362	-102.05278	383119
zamora de hidalgo-16-mx	america/mexico_city	19.98912	-102.28477	315302
lazaro cardenas-16-mx	america/mexico_city	17.98085	-102.22172	139626
heroica zitacuaro-16-mx	america/mexico_city	19.43661	-100.35691	171382
monterrey-19-mx	america/monterrey	25.66667	-100.31667	3531911
tepic-18-mx	america/mazatlan	21.5	-104.9	315119
merida-31-mx	america/merida	20.96667	-89.61667	876195
veracruz-30-mx	america/mexico_city	19.18074	-96.13405	568313
xalapa de enriquez-30-mx	america/mexico_city	19.53333	-96.91667	605638
coatzacoalcos-30-mx	america/mexico_city	18.14212	-94.4371	525786
poza rica de hidalgo-30-mx	america/mexico_city	20.53315	-97.45946	410225
cordoba-30-mx	america/mexico_city	18.88584	-96.93125	394933
tantoyuca-30-mx	america/mexico_city	21.35	-98.23333	103610
temapache-30-mx	america/mexico_city	21.06667	-97.63333	140879
martinez de la torre-30-mx	america/mexico_city	20.06667	-97.05	150330
san andres tuxtla-30-mx	america/mexico_city	18.4487	-95.21327	114576
zacatecas-32-mx	america/mexico_city	22.76843	-102.58141	276384
fresnillo de gonzalez echeverria-32-mx	america/mexico_city	23.17569	-102.86942	105488
maputo-11-mz	africa/maputo	-25.96553	32.58322	1191613
chimoio-10-mz	africa/maputo	-19.11639	33.48333	256936
pemba-01-mz	africa/maputo	-12.97395	40.51775	108737
nampula-06-mz	africa/maputo	-15.11646	39.2666	388526
cidade de nacala-06-mz	africa/maputo	-14.54278	40.67278	224795
lichinga-07-mz	africa/maputo	-13.31278	35.24056	109839
matola-04-mz	africa/maputo	-25.96222	32.45889	543907
beira-05-mz	africa/maputo	-19.84361	34.83889	609252
xai xai-02-mz	africa/maputo	-25.05194	33.64417	212072
tete-08-mz	africa/maputo	-16.15639	33.58667	129316
quelimane-09-mz	africa/maputo	-17.87861	36.88833	188964
maxixe-03-mz	africa/maputo	-23.85972	35.34722	193752
`ajman-02-ae	asia/dubai	25.41111	55.43504	226172
dubai-03-ae	asia/dubai	25.25817	55.30472	1137347
abu dhabi-01-ae	asia/dubai	24.46667	54.36667	603492
al `ayn-01-ae	asia/dubai	24.19167	55.76056	408733
sharjah-06-ae	asia/dubai	25.35731	55.4033	568449
ra's al khaymah-05-ae	asia/dubai	25.78953	55.9432	115949
barcelona-02-ve	america/caracas	10.13333	-64.7	794795
el tigre-02-ve	america/caracas	8.88752	-64.24544	246167
anaco-02-ve	america/caracas	9.43889	-64.47278	117596
caracas-25-ve	america/caracas	10.48801	-66.87919	3000000
catia la mar-26-ve	america/caracas	10.60383	-67.03034	222469
ciudad guayana-06-ve	america/caracas	8.35122	-62.64102	800220
ciudad bolivar-06-ve	america/caracas	8.12923	-63.54086	338000
valencia-07-ve	america/caracas	10.16202	-68.00765	2012994
maracay-04-ve	america/caracas	10.24694	-67.59583	2742491
maracaibo-23-ve	america/caracas	10.63167	-71.64056	2457628
la villa del rosario-23-ve	america/caracas	10.3258	-72.31343	127979
tinaquillo-08-ve	america/caracas	9.91861	-68.30472	159337
merida-14-ve	america/caracas	8.59524	-71.1434	622174
san cristobal-20-ve	america/caracas	7.76694	-72.225	396274
valera-21-ve	america/caracas	9.31778	-70.60361	131866
coro-11-ve	america/caracas	11.4045	-69.67344	195227
punto fijo-11-ve	america/caracas	11.6956	-70.19957	190710
barquisimeto-13-ve	america/caracas	10.07389	-69.32278	885652
calabozo-12-ve	america/caracas	8.92416	-67.42929	117132
petare-15-ve	america/caracas	10.47226	-66.80155	2272407
yaritagua-22-ve	america/caracas	10.08	-69.12611	135566
san felipe-22-ve	america/caracas	10.33991	-68.74247	106954
porlamar-17-ve	america/caracas	10.95796	-63.84906	150460
maturin-16-ve	america/caracas	9.75	-63.17667	410972
cumana-19-ve	america/caracas	10.46354	-64.1775	257783
carupano-19-ve	america/caracas	10.66781	-63.25849	112082
acarigua-18-ve	america/caracas	9.55451	-69.19564	244751
guanare-18-ve	america/caracas	9.04183	-69.74206	112286
alto barinas-05-ve	america/caracas	8.5931	-70.2261	318686
kunduz-24-af	asia/kabul	36.72896	68.857	233433
baghlan-03-af	asia/kabul	36.13068	68.70829	187181
kandahar-23-af	asia/kabul	31.61332	65.71013	391190
ghazni-08-af	asia/kabul	33.55356	68.42689	141000
herat-11-af	asia/kabul	34.34817	62.19967	290290
kabul-13-af	asia/kabul	34.52813	69.17233	3092689
jalalabad-18-af	asia/kabul	34.42647	70.45153	215429
mazar e sharif-30-af	asia/kabul	36.70904	67.11087	418165
gardez-36-af	asia/kabul	33.59744	69.22592	103601
al basrah-02-iq	asia/baghdad	30.53302	47.79747	4830554
umm qasr-02-iq	asia/baghdad	30.0362	47.91951	107620
al faw-02-iq	asia/baghdad	29.97421	48.47309	104569
erbil-11-iq	asia/baghdad	36.19257	44.01062	932800
kirkuk-13-iq	asia/baghdad	35.46806	44.39222	601433
karbala-12-iq	asia/baghdad	32.61603	44.02488	491940
al mawsil al jadidah-15-iq	asia/baghdad	36.33091	43.09065	3857369
baghdad-07-iq	asia/baghdad	33.34058	44.40088	6572513
an najaf al ashraf-17-iq	asia/baghdad	31.9892	44.3291	505765
as sulaymaniyah-05-iq	asia/baghdad	35.56496	45.4329	750286
samarra'-18-iq	asia/baghdad	34.19663	43.8739	243073
sinah-08-iq	asia/baghdad	36.80752	43.03831	223828
an nasiriyah-09-iq	asia/baghdad	31.05799	46.25726	504532
ad diwaniyah-04-iq	asia/baghdad	31.99289	44.92552	429259
ba`qubah-10-iq	asia/baghdad	33.7466	44.64366	273294
al kut-16-iq	asia/baghdad	32.5128	45.81817	393434
al hillah-06-iq	asia/baghdad	32.46367	44.41963	400224
ar ramadi-01-iq	asia/baghdad	33.42056	43.30778	464698
as samawah-03-iq	asia/baghdad	31.33198	45.2944	200138
al `amarah-14-iq	asia/baghdad	31.83588	47.144	358817
reykjavik-39-is	atlantic/reykjavik	64.13548	-21.89541	162352
esfahan-28-ir	asia/tehran	32.65722	51.67761	2281025
kashan-28-ir	asia/tehran	33.98308	51.43644	272359
shahreza-28-ir	asia/tehran	32.03389	51.87944	100790
bojnurd-43-ir	asia/tehran	37.47473	57.32903	251719
shahrud-25-ir	asia/tehran	36.41819	54.97628	131889
semnan-25-ir	asia/tehran	35.57291	53.39714	124826
tehran-26-ir	asia/tehran	35.69439	51.42151	7879802
orumiyeh-01-ir	asia/tehran	37.55274	45.07605	577307
bukan-01-ir	asia/tehran	36.521	46.2089	254773
khvoy-01-ir	asia/tehran	38.5503	44.9521	288923
mahabad-01-ir	asia/tehran	36.7631	45.7222	368781
piranshahr-01-ir	asia/tehran	36.701	45.1413	112634
shiraz-07-ir	asia/tehran	29.61031	52.53114	1348284
zahedan-04-ir	asia/tehran	29.4963	60.8629	551980
iranshahr-04-ir	asia/tehran	27.20245	60.68476	131232
zabol-04-ir	asia/tehran	31.0287	61.5012	121989
khorramabad-23-ir	asia/tehran	33.48778	48.35583	357526
borujerd-23-ir	asia/tehran	33.8973	48.7516	299440
kuhdasht-23-ir	asia/tehran	33.53335	47.60999	100208
karaj-44-ir	asia/tehran	35.83351	50.96556	1661463
hamadan-09-ir	asia/tehran	34.79922	48.51456	1130620
malayer-09-ir	asia/tehran	34.2969	48.8235	252823
mashhad-42-ir	asia/tehran	36.31559	59.56796	2307177
sabzevar-42-ir	asia/tehran	36.2126	57.68191	226183
neyshabur-42-ir	asia/tehran	36.21329	58.79576	220929
torbat e heydariyeh-42-ir	asia/tehran	35.27401	59.21949	125633
quchan-42-ir	asia/tehran	37.106	58.50955	111752
kerman-29-ir	asia/tehran	30.28321	57.07879	577514
sirjan-29-ir	asia/tehran	29.43704	55.68023	207645
rafsanjan-29-ir	asia/tehran	30.4067	55.9939	147680
yazd-40-ir	asia/tehran	31.89722	54.3675	534019
ardakan-40-ir	asia/tehran	32.31001	54.01747	110708
birjand-41-ir	asia/tehran	32.86628	59.22114	196982
shahr e kord-03-ir	asia/tehran	32.32556	50.86444	186615
kahriz-13-ir	asia/tehran	34.3838	47.0553	1387806
harsin-13-ir	asia/tehran	34.2721	47.5861	111061
bandar 'abbas-11-ir	asia/tehran	27.1865	56.2808	447173
ilam-10-ir	asia/tehran	33.6374	46.4227	140940
qom-39-ir	asia/tehran	34.6401	50.8764	900000
qazvin-38-ir	asia/tehran	36.2797	50.0049	405134
ahvaz-15-ir	asia/tehran	31.3203	48.6693	841145
abadan-15-ir	asia/tehran	30.3392	48.3043	738006
masjed soleyman-15-ir	asia/tehran	31.9364	49.3039	189017
behbahan-15-ir	asia/tehran	30.5959	50.2417	101112
bandar bushehr-22-ir	asia/tehran	28.9684	50.8385	251436
sanandaj-16-ir	asia/tehran	35.31495	46.99883	349176
saqqez-16-ir	asia/tehran	36.24992	46.2735	256036
tabriz-33-ir	asia/tehran	38.08	46.2919	1424641
marand-33-ir	asia/tehran	38.4329	45.7749	124191
bonab-33-ir	asia/tehran	37.3404	46.0561	110034
ardabil-32-ir	asia/tehran	38.2498	48.2933	410753
parsabad-32-ir	asia/tehran	39.6482	47.9174	101661
gorgan-37-ir	asia/tehran	36.84165	54.44361	244937
gonbad e qabus-37-ir	asia/tehran	37.25004	55.16721	212706
zanjan-36-ir	asia/tehran	36.6736	48.4787	357471
alvand-36-ir	asia/tehran	36.3187	49.1678	195306
shari i tajan-35-ir	asia/tehran	36.56332	53.06009	711091
amol-35-ir	asia/tehran	36.46961	52.35072	199382
chalus-35-ir	asia/tehran	36.655	51.4204	109638
arak-34-ir	asia/tehran	34.09174	49.68916	503647
saveh-34-ir	asia/tehran	35.0213	50.3566	175533
rasht-08-ir	asia/tehran	37.28077	49.58319	748200
langerud-08-ir	asia/tehran	37.19701	50.15351	115650
yerevan-11-am	asia/yerevan	40.18111	44.51361	1093485
vanadzor-06-am	asia/yerevan	40.80456	44.4939	116157
gyumri-07-am	asia/yerevan	40.7942	43.84528	148381
cagliari-14ca-it	europe/rome	39.20738	9.13462	356390
modena-05mo-it	europe/rome	44.64783	10.92539	437554
foggia-13fg-it	europe/rome	41.46093	15.54925	455901
varese-09va-it	europe/rome	45.82908	8.82193	323100
caserta-04ce-it	europe/rome	41.08322	14.33493	376756
frosinone-07fr-it	europe/rome	41.64002	13.3401	215884
agrigento-15ag-it	europe/rome	37.32084	13.58876	253352
treviso-20tv-it	europe/rome	45.66667	12.245	282419
trento-17tn-it	europe/rome	46.06787	11.12108	155269
napoli-04na-it	europe/rome	40.83333	14.25	2728528
sassari-14ss-it	europe/rome	40.72722	8.56028	185793
cuneo-12cn-it	europe/rome	44.39733	7.54453	161598
torino-12to-it	europe/rome	45.07049	7.68682	1465519
andria-13bt-it	europe/rome	41.23063	16.29087	324049
pesaro-10pu-it	europe/rome	43.90357	12.89026	163885
forli-05fc-it	europe/rome	44.22361	12.05278	220999
san remo-08im-it	europe/rome	43.81725	7.7772	114731
catanzaro-03cz-it	europe/rome	38.89079	16.5987	236040
marsala-15tp-it	europe/rome	37.79664	12.43518	256363
cosenza-03cs-it	europe/rome	39.30999	16.25019	256529
chieti-01ch-it	europe/rome	42.36094	14.13801	133861
ragusa-15rg-it	europe/rome	36.92824	14.71719	249538
arezzo-16ar-it	europe/rome	43.46139	11.87691	169313
ferrara-05fe-it	europe/rome	44.82678	11.62071	236055
monza-09mb-it	europe/rome	45.58248	9.27485	488337
trieste-06ts-it	europe/rome	45.64861	13.78	211184
mantova-09mn-it	europe/rome	45.16031	10.79784	100794
alessandria-12al-it	europe/rome	44.91245	8.61894	212655
milano-09mi-it	europe/rome	45.46427	9.18951	2417258
perugia-18pg-it	europe/rome	43.1122	12.38878	429967
genova-08ge-it	europe/rome	44.40632	8.93386	677670
novara-12no-it	europe/rome	45.44056	8.61684	137140
bolzano-17bz-it	europe/rome	46.49272	11.33358	163922
la spezia-08sp-it	europe/rome	44.11054	9.84339	111450
bari-13ba-it	europe/rome	41.11773	16.85118	1089803
bergamo-09bg-it	europe/rome	45.69798	9.66895	212686
brindisi-13br-it	europe/rome	40.62773	17.93682	272867
ravenna-05ra-it	europe/rome	44.4175	12.20111	261889
l'aquila-01aq-it	europe/rome	42.35055	13.39954	106840
reggio nell'emilia-05re-it	europe/rome	44.69825	10.63125	185320
brescia-09bs-it	europe/rome	45.52478	10.22727	304381
rimini-05rn-it	europe/rome	44.06333	12.58083	197229
reggio calabria-03rc-it	europe/rome	38.11047	15.66129	248400
bologna-05bo-it	europe/rome	44.49381	11.33875	604817
como-09co-it	europe/rome	45.80998	9.08744	150489
padova-20pd-it	europe/rome	45.41519	11.88181	351856
messina-15me-it	europe/rome	38.19327	15.54969	325392
pistoia-16pt-it	europe/rome	43.92125	10.92361	164191
pisa-16pi-it	europe/rome	43.71553	10.39659	209781
firenze-16fi-it	europe/rome	43.76667	11.25	745867
prato-16po-it	europe/rome	43.88425	11.09092	190001
terni-18tr-it	europe/rome	42.56713	12.64987	145793
roma-07rm-it	europe/rome	41.89474	12.4839	3402740
cremona-09cr-it	europe/rome	45.13617	10.02797	103868
macerata-10mc-it	europe/rome	43.29816	13.44108	117873
lecce-13le-it	europe/rome	40.35703	18.17202	268934
taranto-13ta-it	europe/rome	40.47611	17.22972	449058
palermo-15pa-it	europe/rome	38.11582	13.35976	880164
livorno-16li-it	europe/rome	43.54264	10.316	229241
parma-05pr-it	europe/rome	44.80266	10.32898	204787
lucca-16lu-it	europe/rome	43.84357	10.50585	260582
latina-07lt-it	europe/rome	41.46614	12.9043	302330
catania-15ct-it	europe/rome	37.50213	15.08719	762641
pavia-09pv-it	europe/rome	45.18446	9.16145	166847
pescara-01pe-it	europe/rome	42.46024	14.21021	172403
gela-15cl-it	europe/rome	37.08034	14.23068	185007
vicenza-20vi-it	europe/rome	45.55729	11.5409	277719
venezia-20ve-it	europe/rome	45.43861	12.32667	696353
massa-16ms-it	europe/rome	44.02204	10.11409	156803
ancona-10an-it	europe/rome	43.59816	13.51008	256762
siracusa-15sr-it	europe/rome	37.08515	15.273	315609
salerno-04sa-it	europe/rome	40.67797	14.76599	578719
verona-20vr-it	europe/rome	45.43419	10.99779	394070
cao lanh-09-vn	asia/ho_chi_minh	10.45	105.63333	123843
song cau-61-vn	asia/ho_chi_minh	13.45	109.21667	163662
buon ma thuot-88-vn	asia/ho_chi_minh	12.66667	108.05	146975
soc trang-65-vn	asia/ho_chi_minh	9.60333	105.98	114453
hue-66-vn	asia/ho_chi_minh	16.46667	107.6	287217
nam dinh-82-vn	asia/ho_chi_minh	20.41667	106.16667	193499
vinh long-69-vn	asia/ho_chi_minh	10.25	105.96667	103314
can tho-87-vn	asia/ho_chi_minh	10.03333	105.78333	259598
thai nguyen-85-vn	asia/ho_chi_minh	21.59278	105.84417	133877
can duoc-24-vn	asia/ho_chi_minh	10.61667	106.66667	217001
long xuyen-01-vn	asia/ho_chi_minh	10.38639	105.43518	228392
thanh pho ho chi minh-20-vn	asia/ho_chi_minh	10.75	106.66667	3597468
rach gia-21-vn	asia/ho_chi_minh	10.01667	105.08333	228356
da lat-23-vn	asia/ho_chi_minh	11.94646	108.44193	197000
quy nhon-46-vn	asia/ho_chi_minh	13.76667	109.23333	210338
phan thiet-47-vn	asia/ho_chi_minh	10.93333	108.1	321304
ha noi-44-vn	asia/ho_chi_minh	21.0245	105.84117	1522783
vung tau-45-vn	asia/ho_chi_minh	10.34599	107.08426	209683
bien hoa-43-vn	asia/ho_chi_minh	10.95	106.81667	407208
pleiku-49-vn	asia/ho_chi_minh	13.98333	108.0	114225
ca mau-77-vn	asia/ho_chi_minh	9.17694	105.15	111894
thanh pho bac lieu-73-vn	asia/ho_chi_minh	9.29414	105.72776	107911
sa pa-90-vn	asia/ho_chi_minh	22.34023	103.84415	175124
turan-78-vn	asia/ho_chi_minh	16.06778	108.22083	752493
haiphong-13-vn	asia/ho_chi_minh	20.85611	106.68222	602695
vinh-58-vn	asia/ho_chi_minh	18.66667	105.66667	270841
nha trang-54-vn	asia/ho_chi_minh	12.25	109.18333	430212
ha long-30-vn	asia/ho_chi_minh	20.95111	107.08	347372
my tho-37-vn	asia/ho_chi_minh	10.36004	106.35996	122310
hoa binh-53-vn	asia/ho_chi_minh	20.81333	105.33833	105260
thanh hoa-34-vn	asia/ho_chi_minh	19.8	105.76667	166227
san miguel de tucuman-24-ar	america/argentina/tucuman	-26.82414	-65.2226	988579
resistencia-03-ar	america/argentina/cordoba	-27.46056	-58.98389	464726
presidencia roque saenz pena-03-ar	america/argentina/cordoba	-26.78522	-60.43876	166779
la plata-01-ar	america/argentina/buenos_aires	-34.92145	-57.95453	1212955
mar del plata-01-ar	america/argentina/buenos_aires	-38.00228	-57.55754	553935
moron-01-ar	america/argentina/buenos_aires	-34.65344	-58.61975	466304
bahia blanca-01-ar	america/argentina/buenos_aires	-38.7196	-62.27243	333755
san nicolas de los arroyos-01-ar	america/argentina/buenos_aires	-33.33578	-60.22523	127742
tandil-01-ar	america/argentina/buenos_aires	-37.32167	-59.13316	104325
zarate-01-ar	america/argentina/buenos_aires	-34.09814	-59.02858	170393
olavarria-01-ar	america/argentina/buenos_aires	-36.89272	-60.32254	140261
junin-01-ar	america/argentina/buenos_aires	-34.58382	-60.94332	119594
corrientes-06-ar	america/argentina/cordoba	-27.4806	-58.8341	354414
buenos aires-07-ar	america/argentina/buenos_aires	-34.61315	-58.37723	13205935
santiago del estero-22-ar	america/argentina/cordoba	-27.79511	-64.26149	354692
cordoba-05-ar	america/argentina/cordoba	-31.4135	-64.18105	1695691
rio cuarto-05-ar	america/argentina/cordoba	-33.13067	-64.34992	153757
villa maria-05-ar	america/argentina/cordoba	-32.40751	-63.24016	109294
parana-08-ar	america/argentina/cordoba	-31.73197	-60.5238	300136
concordia-08-ar	america/argentina/cordoba	-31.39296	-58.02089	145210
formosa-09-ar	america/argentina/cordoba	-26.17753	-58.17814	221383
san fernando del valle de catamarca-02-ar	america/argentina/catamarca	-28.46957	-65.78524	188812
posadas-14-ar	america/argentina/cordoba	-27.36708	-55.89608	340874
santa rosa-11-ar	america/argentina/salta	-36.61667	-64.28333	111424
san salvador de jujuy-10-ar	america/argentina/jujuy	-24.19456	-65.29712	412520
mendoza-13-ar	america/argentina/mendoza	-32.89084	-68.82717	959433
san rafael-13-ar	america/argentina/mendoza	-34.61772	-68.33007	109163
la rioja-12-ar	america/argentina/la_rioja	-29.41105	-66.85067	162620
neuquen-15-ar	america/argentina/salta	-38.95161	-68.0591	296234
comodoro rivadavia-04-ar	america/argentina/catamarca	-45.86667	-67.5	140850
trelew-04-ar	america/argentina/catamarca	-43.24895	-65.30505	119777
salta-17-ar	america/argentina/salta	-24.7859	-65.41166	512686
cipolletti-16-ar	america/argentina/salta	-38.93392	-67.99032	194192
san luis-19-ar	america/argentina/san_luis	-33.29501	-66.33563	183982
san juan-18-ar	america/argentina/san_juan	-31.5375	-68.53639	678525
rosario-21-ar	america/argentina/cordoba	-32.94682	-60.63932	1412004
santa fe de la vera cruz-21-ar	america/argentina/cordoba	-31.63333	-60.7	601437
reconquista-21-ar	america/argentina/cordoba	-29.15	-59.65	113261
rafaela-21-ar	america/argentina/cordoba	-31.25033	-61.4867	107470
sydney-02-au	australia/sydney	-33.86785	151.20732	4972819
newcastle-02-au	australia/sydney	-32.92715	151.77647	540348
wollongong-02-au	australia/sydney	-34.424	150.89345	260914
north shore-02-au	australia/sydney	-31.40237	152.90185	255788
albury-02-au	australia/sydney	-36.07494	146.92394	104258
port au prince-11-au	prince	18.53917	-72.335	2893870
petit goave-11-au	prince	18.43139	-72.86694	117504
jacmel-13-au	prince	18.23417	-72.53472	137966
canberra-01-au	australia/sydney	-35.28346	149.12807	327700
melbourne-07-au	australia/melbourne	-37.814	144.96332	4294865
geelong-07-au	australia/melbourne	-38.14711	144.36069	311428
brisbane-04-au	australia/brisbane	-27.46794	153.02809	1377071
gold coast-04-au	australia/brisbane	-28.00029	153.43088	615828
cairns-04-au	australia/brisbane	-16.92304	145.76625	154225
townsville-04-au	australia/brisbane	-19.26639	146.8057	138954
adelaide-05-au	australia/adelaide	-34.92866	138.59863	1173570
darwin-03-au	australia/darwin	-12.46113	130.84185	118080
perth-08-au	australia/perth	-31.95224	115.8614	1507356
cap haitien-09-au	prince	19.75778	-72.20417	205199
les cayes-12-au	prince	18.2	-73.75	125799
gonaives-06-au	prince	19.45	-72.68333	199911
vienna-09900-at	europe/vienna	48.20849	16.37208	1691468
graz-06-at	europe/vienna	47.06667	15.45	222326
innsbruck-07-at	europe/vienna	47.26266	11.39454	112467
linz-04-at	europe/vienna	48.30639	14.28611	181162
salzburg-05-at	europe/vienna	47.79941	13.04399	165942
babijn-00-aw	america/aruba	12.53333	-69.98333	100067
hyderabad-02-in	asia/kolkata	17.37528	78.47444	5363046
vishakhapatnam-02-in	asia/kolkata	17.69004	83.20925	1533379
vijayawada-02-in	asia/kolkata	16.51667	80.61667	1920501
warangal-02-in	asia/kolkata	18.0	79.58333	557802
nellore-02-in	asia/kolkata	14.43333	79.96667	532490
nizamabad-02-in	asia/kolkata	18.66667	78.11667	473083
rajahmundry-02-in	asia/kolkata	16.98333	81.78333	1097606
tirupati-02-in	asia/kolkata	13.65	79.41667	429414
anantapur-02-in	asia/kolkata	14.68333	77.6	387987
ramagundam-02-in	asia/kolkata	18.755	79.474	739196
machilipatnam-02-in	asia/kolkata	16.16667	81.13333	373107
eluru-02-in	asia/kolkata	16.7	81.1	366767
vizianagaram-02-in	asia/kolkata	18.11667	83.41667	233088
proddatur-02-in	asia/kolkata	14.73333	78.55	474219
ongole-02-in	asia/kolkata	15.5	80.05	397885
khammam-02-in	asia/kolkata	17.25	80.15	367939
nandyal-02-in	asia/kolkata	15.48333	78.48333	334701
adoni-02-in	asia/kolkata	15.63333	77.28333	260019
mahbubnagar-02-in	asia/kolkata	16.73333	77.98333	220756
hindupur-02-in	asia/kolkata	13.82889	77.49333	153518
nalgonda-02-in	asia/kolkata	17.05	79.26667	334789
guntakal-02-in	asia/kolkata	15.16667	77.38333	120964
adilabad-02-in	asia/kolkata	19.66667	78.53333	180763
srikakulam-02-in	asia/kolkata	18.3	83.9	235750
madanapalle-02-in	asia/kolkata	13.55	78.5	199637
jagtial-02-in	asia/kolkata	18.8	78.93333	253685
narasaraopet-02-in	asia/kolkata	16.25	80.06667	252531
rayachoti-02-in	asia/kolkata	14.05	78.75	112512
nirmal-02-in	asia/kolkata	19.1	78.35	127102
kottagudem-02-in	asia/kolkata	17.55	80.63333	341227
bapatla-02-in	asia/kolkata	15.9	80.46667	183791
palasa-02-in	asia/kolkata	18.76667	84.41667	162948
markapur-02-in	asia/kolkata	15.73333	79.28333	143096
tandur-02-in	asia/kolkata	17.23333	77.58333	106576
narasapur-02-in	asia/kolkata	16.45	81.66667	169337
bobbili-02-in	asia/kolkata	18.56667	83.36667	155134
pithapuram-02-in	asia/kolkata	17.11667	82.26667	142263
chennai-25-in	asia/kolkata	13.08784	80.27847	5955391
teni-25-in	asia/kolkata	10.0	77.48333	1455238
coimbatore-25-in	asia/kolkata	10.9925	76.96139	1893113
madurai-25-in	asia/kolkata	9.93333	78.11667	1282209
salem-25-in	asia/kolkata	11.65	78.16667	1228751
tiruchchirappalli-25-in	asia/kolkata	10.805	78.68556	1034609
tirunelveli-25-in	asia/kolkata	8.73333	77.7	820520
thanjavur-25-in	asia/kolkata	10.8	79.15	574834
nagercoil-25-in	asia/kolkata	8.19389	77.43139	298316
dindigul-25-in	asia/kolkata	10.36896	77.98036	261084
vellore-25-in	asia/kolkata	12.9184	79.13255	661786
cuddalore-25-in	asia/kolkata	11.75	79.75	459281
kanchipuram-25-in	asia/kolkata	12.83515	79.70006	461812
erode-25-in	asia/kolkata	11.3428	77.72741	381953
tiruvannamalai-25-in	asia/kolkata	12.22662	79.07461	212014
rajapalaiyam-25-in	asia/kolkata	9.45296	77.55335	629530
hosur-25-in	asia/kolkata	12.73647	77.83264	189501
nagappattinam-25-in	asia/kolkata	10.76667	79.83333	292761
karaikkudi-25-in	asia/kolkata	10.06667	78.78333	185565
valparai-25-in	asia/kolkata	10.32691	76.95116	148924
vaniyambadi-25-in	asia/kolkata	12.68162	78.62014	148604
paramagudi-25-in	asia/kolkata	9.54633	78.5907	181477
dharapuram-25-in	asia/kolkata	10.73828	77.53223	138376
dharmapuri-25-in	asia/kolkata	12.1277	78.15794	121810
vriddhachalam-25-in	asia/kolkata	11.5	79.33333	151826
agartala-26-in	asia/kolkata	23.83605	91.27939	244552
port blair-01-in	asia/kolkata	11.66667	92.75	112050
kohima-20-in	asia/kolkata	25.67467	94.11099	146123
delhi-07-in	asia/kolkata	28.65381	77.22897	11991029
puducherry-22-in	asia/kolkata	11.93	79.83	227411
ludhiana-23-in	asia/kolkata	30.90015	75.85229	2197140
amritsar-23-in	asia/kolkata	31.63661	74.87476	1371332
jalandhar-23-in	asia/kolkata	31.32556	75.57917	1114067
patiala-23-in	asia/kolkata	30.32715	76.40266	738732
bhatinda-23-in	asia/kolkata	30.20712	74.9414	565212
pathankot-23-in	asia/kolkata	32.27306	75.65256	265752
abohar-23-in	asia/kolkata	30.1431	74.19749	291323
moga-23-in	asia/kolkata	30.81571	75.17419	279100
barnala-23-in	asia/kolkata	30.37205	75.54537	464151
firozpur-23-in	asia/kolkata	30.92574	74.61311	147981
rupnagar-23-in	asia/kolkata	30.96878	76.52557	180945
ahmadabad-09-in	asia/kolkata	23.03333	72.61667	4518521
surat-09-in	asia/kolkata	21.16667	72.83333	3597788
vadodara-09-in	asia/kolkata	22.3	73.2	2020531
rajkot-09-in	asia/kolkata	22.3	70.78333	1394957
bhavnagar-09-in	asia/kolkata	21.76667	72.15	712105
jamnagar-09-in	asia/kolkata	22.46667	70.06667	563651
junagadh-09-in	asia/kolkata	21.51667	70.46667	607994
surendranagar-09-in	asia/kolkata	22.7	71.68333	342371
veraval-09-in	asia/kolkata	20.9	70.36667	257245
bharuch-09-in	asia/kolkata	21.7	72.96667	228270
porbandar-09-in	asia/kolkata	21.64219	69.60929	202583
bhuj-09-in	asia/kolkata	23.25397	69.66928	215567
godhra-09-in	asia/kolkata	22.75	73.63333	372181
palanpur-09-in	asia/kolkata	24.17097	72.43821	487901
morbi-09-in	asia/kolkata	22.81667	70.83333	186735
botad-09-in	asia/kolkata	22.16667	71.66667	145664
amreli-09-in	asia/kolkata	21.61667	71.23333	394979
khambhat-09-in	asia/kolkata	22.3	72.61667	100731
valsad-09-in	asia/kolkata	20.63333	72.93333	192954
visnagar-09-in	asia/kolkata	23.69855	72.5521	169122
kolkata-28-in	asia/kolkata	22.56263	88.36304	11682985
durgapur-28-in	asia/kolkata	23.48333	87.31667	1697116
shiliguri-28-in	asia/kolkata	26.71004	88.42851	940744
kulti-28-in	asia/kolkata	23.73333	86.85	428833
barddhaman-28-in	asia/kolkata	23.24056	87.86944	484174
gosaba-28-in	asia/kolkata	22.16547	88.8007	262877
kharagpur-28-in	asia/kolkata	22.33333	87.33333	452665
baharampur-28-in	asia/kolkata	24.10473	88.25155	492777
haldia-28-in	asia/kolkata	22.06046	88.10975	349393
raiganj-28-in	asia/kolkata	25.61281	88.12449	302601
ingraj bazar-28-in	asia/kolkata	25.00447	88.14573	288654
jaigaon-28-in	asia/kolkata	26.84766	89.37558	356309
shantipur-28-in	asia/kolkata	23.24722	88.43302	684097
balurghat-28-in	asia/kolkata	25.22099	88.77732	141404
puruliya-28-in	asia/kolkata	23.33333	86.36667	178568
kishanganj-28-in	asia/kolkata	26.10282	87.95205	150498
koch bihar-28-in	asia/kolkata	26.32539	89.44508	164180
siuri-28-in	asia/kolkata	23.91667	87.53333	107880
jaipur-24-in	asia/kolkata	26.91962	75.78781	2794880
jodhpur-24-in	asia/kolkata	26.26841	73.00594	921476
kota-24-in	asia/kolkata	25.18254	75.83906	972262
bikaner-24-in	asia/kolkata	28.02094	73.30749	614485
ajmer-24-in	asia/kolkata	26.44976	74.64116	717580
udaipur-24-in	asia/kolkata	24.57117	73.69183	462210
bhilwara-24-in	asia/kolkata	25.34644	74.63523	418398
alwar-24-in	asia/kolkata	27.56246	76.625	447541
ganganagar-24-in	asia/kolkata	29.92008	73.87496	271896
bharatpur-24-in	asia/kolkata	27.21731	77.49009	391956
pali-24-in	asia/kolkata	25.77276	73.32335	252659
sikar-24-in	asia/kolkata	27.61206	75.13996	531097
hanumangarh-24-in	asia/kolkata	29.58182	74.32938	223458
tonk-24-in	asia/kolkata	26.16638	75.78824	254073
beawar-24-in	asia/kolkata	26.10119	74.32028	231997
gangapur-24-in	asia/kolkata	26.47249	76.71744	320905
jhunjhunun-24-in	asia/kolkata	28.12559	75.39797	361382
sawai madhopur-24-in	asia/kolkata	26.02301	76.34408	137075
chittaurgarh-24-in	asia/kolkata	24.88963	74.62403	185631
dhaulpur-24-in	asia/kolkata	26.69286	77.87968	189225
nagaur-24-in	asia/kolkata	27.20201	73.73394	215433
makrana-24-in	asia/kolkata	27.04361	74.72445	258758
baran-24-in	asia/kolkata	25.1	76.51667	131216
sardarshahr-24-in	asia/kolkata	28.44062	74.491	210407
dausa-24-in	asia/kolkata	26.89	76.33584	111728
balotra-24-in	asia/kolkata	25.83242	72.24	108102
rajsamand-24-in	asia/kolkata	25.07145	73.8798	106480
jhalawar-24-in	asia/kolkata	24.59676	76.16503	176133
abu road-24-in	asia/kolkata	24.48012	72.78186	137082
guwahati-03-in	asia/kolkata	26.18617	91.75095	983846
silchar-03-in	asia/kolkata	24.82733	92.79787	223406
dimapur-03-in	asia/kolkata	25.91174	93.7217	231825
dibrugarh-03-in	asia/kolkata	27.47989	94.90837	250604
jorhat-03-in	asia/kolkata	26.75751	94.20306	189149
bongaigaon-03-in	asia/kolkata	26.47703	90.55815	321933
tezpur-03-in	asia/kolkata	26.63333	92.8	119687
dehra dun-39-in	asia/kolkata	30.31667	78.03333	876422
haldwani-39-in	asia/kolkata	29.22254	79.5286	368394
roorkee-39-in	asia/kolkata	29.86313	77.89126	123164
kashipur-39-in	asia/kolkata	29.21398	78.95693	145662
ranchi-38-in	asia/kolkata	23.35	85.33333	1035404
jamshedpur-38-in	asia/kolkata	22.8	86.18333	831845
bokaro-38-in	asia/kolkata	23.78333	85.96667	1129234
hazaribag-38-in	asia/kolkata	23.98333	85.35	140063
daltenganj-38-in	asia/kolkata	24.04306	84.06866	118366
giridih-38-in	asia/kolkata	24.18561	86.30772	110671
bhubaneshwar-21-in	asia/kolkata	20.23333	85.83333	1728135
brahmapur-21-in	asia/kolkata	19.31667	84.78333	410339
sambalpur-21-in	asia/kolkata	21.45	83.96667	493860
balasore-21-in	asia/kolkata	21.49417	86.93167	245006
bhadrakh-21-in	asia/kolkata	21.05278	86.52	140805
balangir-21-in	asia/kolkata	20.71667	83.48333	129591
paradip garh-21-in	asia/kolkata	20.31667	86.61667	164111
jaypur-21-in	asia/kolkata	18.85	82.58333	122007
bhawanipatna-21-in	asia/kolkata	19.9	83.16667	110867
shimla-11-in	asia/kolkata	31.10442	77.16662	268583
gorakhpur-10-in	asia/kolkata	29.44702	75.67181	1964073
faridabad-10-in	asia/kolkata	28.41252	77.31977	1745818
rohtak-10-in	asia/kolkata	28.88838	76.5754	984549
panipat-10-in	asia/kolkata	29.39005	76.96949	661330
yamunanagar-10-in	asia/kolkata	30.12913	77.28049	547437
sirsa-10-in	asia/kolkata	29.53489	75.02898	269415
jind-10-in	asia/kolkata	29.31617	76.31436	177559
ambala-10-in	asia/kolkata	30.36284	76.79516	218050
kaithal-10-in	asia/kolkata	29.8019	76.39667	158137
rewari-10-in	asia/kolkata	28.19721	76.61757	179187
dabwali-10-in	asia/kolkata	29.94878	74.73707	100751
thiruvananthapuram-13-in	asia/kolkata	8.50694	76.95694	1049352
cochin-13-in	asia/kolkata	9.93988	76.26022	1179604
calicut-13-in	asia/kolkata	11.25	75.76667	889958
kollam-13-in	asia/kolkata	8.88056	76.59167	601846
trichur-13-in	asia/kolkata	10.51667	76.21667	647559
alleppey-13-in	asia/kolkata	9.49004	76.3264	310479
palakkad-13-in	asia/kolkata	10.7725	76.65139	215257
thalassery-13-in	asia/kolkata	11.74778	75.48833	440129
payyannur-13-in	asia/kolkata	12.1	75.2	217233
srinagar-12-in	asia/kolkata	34.08842	74.80298	1313078
jammu-12-in	asia/kolkata	32.73569	74.86911	572907
imphal-17-in	asia/kolkata	24.80805	93.9442	337696
mumbai-16-in	asia/kolkata	19.07283	72.88261	22179466
pune-16-in	asia/kolkata	18.51957	73.85535	5505410
nagpur-16-in	asia/kolkata	21.15	79.1	2438453
raigarh fort-16-in	asia/kolkata	18.25	73.43333	2351346
nasik-16-in	asia/kolkata	19.98333	73.8	1479041
aurangabad-16-in	asia/kolkata	19.88333	75.33333	1143022
solapur-16-in	asia/kolkata	17.68333	75.91667	1089364
amravati-16-in	asia/kolkata	20.93333	77.75	850826
sangli-16-in	asia/kolkata	16.85438	74.56417	1635226
malegaon-16-in	asia/kolkata	20.55	74.53333	957305
jalgaon-16-in	asia/kolkata	21.01667	75.56667	971075
akola-16-in	asia/kolkata	20.73333	77.0	752121
ahmadnagar-16-in	asia/kolkata	19.08333	74.73333	459134
latur-16-in	asia/kolkata	18.4	76.58333	531951
chandrapur-16-in	asia/kolkata	19.95	79.3	645718
parbhani-16-in	asia/kolkata	19.26667	76.78333	588426
jalna-16-in	asia/kolkata	19.83333	75.88333	349559
yavatmal-16-in	asia/kolkata	20.4	78.13333	223945
gondia-16-in	asia/kolkata	21.45	80.2	168115
wardha-16-in	asia/kolkata	20.75	78.61667	253164
satara-16-in	asia/kolkata	17.68333	73.98333	163010
barsi-16-in	asia/kolkata	18.23333	75.7	238178
udgir-16-in	asia/kolkata	18.38333	77.11667	129711
nandurbar-16-in	asia/kolkata	21.36667	74.25	246437
amalner-16-in	asia/kolkata	21.05	75.06667	166909
pandharpur-16-in	asia/kolkata	17.66667	75.33333	126944
parli vaijnath-16-in	asia/kolkata	18.85	76.53333	161768
bhandara-16-in	asia/kolkata	21.16667	79.65	132497
hingoli-16-in	asia/kolkata	19.71667	77.15	287927
palghar-16-in	asia/kolkata	19.68333	72.75	152549
sangamner-16-in	asia/kolkata	19.56667	74.21667	164403
buldana-16-in	asia/kolkata	20.53333	76.18333	224294
karanja-16-in	asia/kolkata	20.48333	77.48333	135486
khopoli-16-in	asia/kolkata	18.78333	73.33333	157576
nipani-16-in	asia/kolkata	16.4	74.38333	102664
baramati-16-in	asia/kolkata	18.15	74.58333	152561
bangalore-19-in	asia/kolkata	12.97194	77.59369	5614000
mysore-19-in	asia/kolkata	12.29791	76.63925	1231896
hubli-19-in	asia/kolkata	15.34776	75.13378	1185874
gulbarga-19-in	asia/kolkata	17.33333	76.83333	656529
belgaum-19-in	asia/kolkata	15.85212	74.50447	641016
mangalore-19-in	asia/kolkata	12.91723	74.85603	769831
bellary-19-in	asia/kolkata	15.15	76.93333	427868
shimoga-19-in	asia/kolkata	13.93157	75.56791	607125
tumkur-19-in	asia/kolkata	13.34222	77.10167	444667
bijapur-19-in	asia/kolkata	16.82442	75.71537	335966
raichur-19-in	asia/kolkata	16.2	77.36667	267609
bidar-19-in	asia/kolkata	17.9	77.55	321605
hospet-19-in	asia/kolkata	15.26667	76.4	387939
gadag-19-in	asia/kolkata	15.42977	75.62971	224391
chitradurga-19-in	asia/kolkata	14.22262	76.40038	301564
robertsonpet-19-in	asia/kolkata	12.96667	78.28333	377670
hassan-19-in	asia/kolkata	13.00056	76.09944	422534
ranibennur-19-in	asia/kolkata	14.61667	75.61667	326678
bagalkot-19-in	asia/kolkata	16.18673	75.69614	291977
rabkavi-19-in	asia/kolkata	16.46667	75.1	273343
chintamani-19-in	asia/kolkata	13.4	78.06667	178743
sindhnur-19-in	asia/kolkata	15.78333	76.76667	137716
chamrajnagar-19-in	asia/kolkata	11.92312	76.93949	151686
channapatna-19-in	asia/kolkata	12.65	77.21667	145540
yadgir-19-in	asia/kolkata	16.76667	77.13333	199669
sirsi-19-in	asia/kolkata	14.61667	74.85	107554
ilkal-19-in	asia/kolkata	15.96667	76.13333	140649
bhatkal-19-in	asia/kolkata	13.96667	74.56667	132079
shillong-18-in	asia/kolkata	25.56892	91.88313	132842
aizawl-31-in	asia/kolkata	23.7367	92.7146	265331
chandigarh-05-in	asia/kolkata	30.73629	76.7884	914371
raipur-37-in	asia/kolkata	21.23333	81.63333	1616253
korba-37-in	asia/kolkata	22.35	82.68333	523405
bilaspur-37-in	asia/kolkata	22.08333	82.15	442222
raj nandgaon-37-in	asia/kolkata	21.1	81.03333	206034
raigarh-37-in	asia/kolkata	21.9	83.4	139534
dhamtari-37-in	asia/kolkata	20.70722	81.54972	113135
kanpur-36-in	asia/kolkata	26.4478	80.34627	3107119
lucknow-36-in	asia/kolkata	26.83928	80.92313	2706827
agra-36-in	asia/kolkata	27.18333	78.01667	2506267
meerut-36-in	asia/kolkata	28.97155	77.71934	3752922
varanasi-36-in	asia/kolkata	25.31668	83.01042	1730175
allahabad-36-in	asia/kolkata	25.44894	81.83328	1226691
aligarh-36-in	asia/kolkata	27.88334	78.07475	1135550
bareilly-36-in	asia/kolkata	28.34702	79.42193	1634265
moradabad-36-in	asia/kolkata	28.83893	78.77684	1990101
gorakhpur-36-in	asia/kolkata	26.75479	83.37235	952977
saharanpur-36-in	asia/kolkata	29.9679	77.54522	844002
jhansi-36-in	asia/kolkata	25.45446	78.58221	448465
muzaffarnagar-36-in	asia/kolkata	29.47394	77.70414	809781
shahjahanpur-36-in	asia/kolkata	27.88142	79.9109	582179
greater noida-36-in	asia/kolkata	28.49615	77.53601	859807
etawah-36-in	asia/kolkata	26.7778	79.02159	441199
mau-36-in	asia/kolkata	25.94167	83.56111	745371
farrukhabad-36-in	asia/kolkata	27.39048	79.58006	539785
rae bareli-36-in	asia/kolkata	26.2191	81.24499	212159
bahraich-36-in	asia/kolkata	27.5743	81.59588	268090
jaunpur-36-in	asia/kolkata	25.75506	82.68361	280583
fatehpur-36-in	asia/kolkata	25.93036	80.8139	218145
sitapur-36-in	asia/kolkata	27.56192	80.68265	538080
orai-36-in	asia/kolkata	25.99074	79.45315	420150
faizabad-36-in	asia/kolkata	26.77691	82.13292	356938
banda-36-in	asia/kolkata	25.47534	80.3358	261001
lalitpur-36-in	asia/kolkata	24.69054	78.41888	201199
hardoi-36-in	asia/kolkata	27.39433	80.1311	226522
basti-36-in	asia/kolkata	26.79446	82.73285	279979
sultanpur-36-in	asia/kolkata	26.25996	82.07314	184360
shikohabad-36-in	asia/kolkata	27.10813	78.58675	194297
kasganj-36-in	asia/kolkata	27.80544	78.64602	359115
mahoba-36-in	asia/kolkata	25.29222	79.87231	133027
najibabad-36-in	asia/kolkata	29.61207	78.34338	383117
balrampur-36-in	asia/kolkata	27.42766	82.1871	143375
chandpur-36-in	asia/kolkata	29.13506	78.26887	181452
renukut-36-in	asia/kolkata	24.21641	83.0358	118523
vrindavan-36-in	asia/kolkata	27.57823	77.69806	101499
gola gokarannath-36-in	asia/kolkata	28.07837	80.47054	113151
jahangirabad-36-in	asia/kolkata	28.40338	78.10562	120319
indore-35-in	asia/kolkata	22.71792	75.8333	2183246
bhopal-35-in	asia/kolkata	23.25469	77.40289	1807164
jabalpur-35-in	asia/kolkata	23.16697	79.95006	1168556
gwalior-35-in	asia/kolkata	26.22982	78.17337	1254700
ujjain-35-in	asia/kolkata	23.18333	75.76667	619551
punasa-35-in	asia/kolkata	22.23333	76.4	604530
mandu-35-in	asia/kolkata	22.36667	75.38333	482740
satna-35-in	asia/kolkata	24.58224	80.8248	542742
sagar-35-in	asia/kolkata	23.83333	78.71667	443030
ratlam-35-in	asia/kolkata	23.33033	75.04032	354661
burhanpur-35-in	asia/kolkata	21.3	76.23333	254676
murwara-35-in	asia/kolkata	23.85	80.4	195856
singrauli-35-in	asia/kolkata	24.19973	82.67535	185580
bhind-35-in	asia/kolkata	26.56672	78.78728	298077
shivpuri-35-in	asia/kolkata	25.42348	77.66067	224549
guna-35-in	asia/kolkata	24.64761	77.31191	322949
vidisha-35-in	asia/kolkata	23.52435	77.80972	209323
chhindwara-35-in	asia/kolkata	22.06667	78.93333	223578
mandsaur-35-in	asia/kolkata	24.07184	75.06986	124988
damoh-35-in	asia/kolkata	23.83333	79.45	164772
chhatarpur-35-in	asia/kolkata	24.91422	79.5878	191009
hoshangabad-35-in	asia/kolkata	22.75	77.71667	296556
seoni-35-in	asia/kolkata	22.08333	79.53333	116700
khargon-35-in	asia/kolkata	21.81667	75.6	129702
betul-35-in	asia/kolkata	21.91528	77.89611	160377
datia-35-in	asia/kolkata	25.67249	78.45815	134692
shahdol-35-in	asia/kolkata	23.28333	81.35	166152
balaghat-35-in	asia/kolkata	21.8	80.18333	104160
sendhwa-35-in	asia/kolkata	21.68333	75.1	126159
shajapur-35-in	asia/kolkata	23.42688	76.27772	170763
narsimhapur-35-in	asia/kolkata	22.95	79.2	116739
biaora-35-in	asia/kolkata	23.86667	76.91667	114545
patna-34-in	asia/kolkata	25.60222	85.11936	2569518
gaya-34-in	asia/kolkata	24.79686	85.00385	637616
bhagalpur-34-in	asia/kolkata	25.24446	86.97183	616883
muzaffarpur-34-in	asia/kolkata	26.12259	85.39055	468051
darbhanga-34-in	asia/kolkata	26.15216	85.89707	418796
bihar sharif-34-in	asia/kolkata	25.19729	85.52374	591267
munger-34-in	asia/kolkata	25.37556	86.47352	488750
purnia-34-in	asia/kolkata	25.77895	87.47422	568873
saharsa-34-in	asia/kolkata	25.88504	86.59471	273456
dehri-34-in	asia/kolkata	24.90504	84.18289	370588
bettiah-34-in	asia/kolkata	26.8024	84.49873	466263
siwan-34-in	asia/kolkata	26.22152	84.35879	207050
bagaha-34-in	asia/kolkata	27.09918	84.09003	103855
buxar-34-in	asia/kolkata	25.57473	83.97867	193523
baruni-34-in	asia/kolkata	25.47446	85.96681	152659
jamui-34-in	asia/kolkata	24.92589	86.22574	116805
sitamarhi-34-in	asia/kolkata	26.59356	85.4906	146449
marmagao-33-in	asia/kolkata	15.4	73.8	519106
ganja-20-az	asia/baku	40.68278	46.36056	303268
baku-09-az	asia/baku	40.37767	49.89201	1539309
sumqayit-54-az	asia/baku	40.58972	49.66861	284169
cork-m04-ie	europe/dublin	51.89797	-8.47061	190384
dun laoghaire-l34-ie	europe/dublin	53.29395	-6.13586	185400
dublin-l33-ie	europe/dublin	53.33306	-6.24889	1024027
kendari-22-id	asia/makassar	-3.945	122.49889	195006
padang-24-id	asia/jakarta	-0.94924	100.35427	980907
payakumbuh-24-id	asia/jakarta	-0.22019	100.63078	220318
bengkulu-03-id	asia/jakarta	-3.80044	102.26554	355957
medan-26-id	asia/jakarta	3.58333	98.66667	2813062
pematangsiantar-26-id	asia/jakarta	2.9595	99.0687	327144
tanjungbalai-26-id	asia/jakarta	2.96667	99.8	297563
rantauprapat-26-id	asia/jakarta	2.1	99.83333	103009
padangsidempuan-26-id	asia/jakarta	1.36667	99.26667	100561
banda aceh-01-id	asia/jakarta	5.5577	95.3222	275276
lhokseumawe-01-id	asia/jakarta	5.1801	97.1507	114767
semarang-07-id	asia/jakarta	-6.9932	110.4203	1847691
surakarta-07-id	asia/jakarta	-7.55611	110.83167	1420032
pekalongan-07-id	asia/jakarta	-6.8886	109.6753	678374
tegal-07-id	asia/jakarta	-6.8694	109.1402	537739
purwokerto-07-id	asia/jakarta	-7.42139	109.23444	510048
purwodadi-07-id	asia/jakarta	-7.0868	110.9158	544521
batang-07-id	asia/jakarta	-6.4846	110.7083	141950
magelang-07-id	asia/jakarta	-7.47056	110.21778	350533
cepu-07-id	asia/jakarta	-7.1475	111.5906	106866
jakarta-04-id	asia/jakarta	-6.21462	106.84513	8540121
jambi-05-id	asia/jakarta	-1.6	103.61667	420323
surabaya-08-id	asia/jakarta	-7.24917	112.75083	3427777
malang-08-id	asia/jakarta	-7.9797	112.6304	1226663
situbondo-08-id	asia/jakarta	-7.70623	114.00976	846417
jember-08-id	asia/jakarta	-8.16604	113.70317	341631
kediri-08-id	asia/jakarta	-7.81667	112.01667	970687
madiun-08-id	asia/jakarta	-7.6298	111.5239	265125
probolinggo-08-id	asia/jakarta	-7.7543	113.2159	333530
banyuwangi-08-id	asia/jakarta	-8.2325	114.35755	369751
pamekasan-08-id	asia/jakarta	-7.1568	113.4746	230372
bojonegoro-08-id	asia/jakarta	-7.1502	111.8817	189848
ambon-28-id	asia/jayapura	-3.69543	128.1814	355596
ternate-29-id	asia/jayapura	0.8	127.4	101731
tanjungpinang-40-id	asia/jakarta	0.91667	104.45	125472
mamuju-41-id	asia/makassar	-2.6748	118.8885	938254
denpasar-02-id	asia/makassar	-8.65	115.21667	557680
singaraja-02-id	asia/makassar	-8.112	115.08818	247824
sorong-39-id	asia/jayapura	-0.88333	131.25	125535
sumedang utara-00-id	asia/jakarta	-6.85	107.91667	206746
pangkalpinang-00-id	asia/jakarta	-2.13333	106.13333	125933
dukuhturi-00-id	asia/jakarta	-6.9	109.08333	346692
melati-00-id	asia/jakarta	-7.73333	110.36667	162517
banjarmasin-12-id	asia/makassar	-3.32442	114.591	704286
barabai-12-id	asia/makassar	-2.58333	115.38333	115752
palu-21-id	asia/makassar	-0.8917	119.8707	282431
pontianak-11-id	asia/pontianak	-0.03333	109.33333	455173
singkawang-11-id	asia/pontianak	0.9	109.0	101838
yogyakarta-10-id	asia/jakarta	-7.78278	110.36083	1282259
palangkaraya-13-id	asia/pontianak	-2.2	113.83333	148139
makassar-38-id	asia/makassar	-5.14	119.4221	1404767
bandarlampung-15-id	asia/jakarta	-5.42544	105.25803	949874
city of balikpapan-14-id	asia/makassar	-1.24204	116.89419	1133866
samarinda-14-id	asia/makassar	-0.5	117.15	567976
bontang-14-id	asia/makassar	0.13333	117.5	101691
mataram-17-id	asia/makassar	-8.58333	116.11667	353857
curug-33-id	asia/jakarta	-6.26583	106.55639	575399
palembang-32-id	asia/jakarta	-2.91673	104.7458	1441500
lubuklinggau-32-id	asia/jakarta	-3.3	102.86667	148243
baturaja-32-id	asia/jakarta	-4.12891	104.16695	134759
perabumulih-32-id	asia/jakarta	-3.45	104.25	103470
pagaralam-32-id	asia/jakarta	-4.01667	103.26667	136292
manado-31-id	asia/makassar	1.487	124.8455	650198
bandung-30-id	asia/jakarta	-6.90389	107.61861	3517271
bekasi-30-id	asia/jakarta	-6.2349	106.9896	6923823
masjid jamie baitul muttaqien-30-id	asia/jakarta	-6.36836	107.9558	1310563
sukabumi-30-id	asia/jakarta	-6.91806	106.92667	500225
tasikmalaya-30-id	asia/jakarta	-7.3274	108.2207	632368
cirebon-30-id	asia/jakarta	-6.7063	108.557	1341492
cikupa-30-id	asia/jakarta	-6.23639	106.50833	438457
cikampek-30-id	asia/jakarta	-6.41972	107.45583	145620
pekanbaru-37-id	asia/jakarta	0.53333	101.45	703956
dumai-37-id	asia/jakarta	1.68333	101.45	143760
jayapura-36-id	asia/jayapura	-2.53333	140.7	134895
gorontalo-34-id	asia/makassar	0.5412	123.0595	144195
kupang-18-id	asia/makassar	-10.1718	123.6075	282396
labuhanbajo-18-id	asia/makassar	-8.4964	119.8877	188724
masaya-11-ni	america/managua	11.97444	-86.09417	151565
managua-10-ni	america/managua	12.13282	-86.2504	1216558
matagalpa-12-ni	america/managua	12.92559	-85.91747	109089
granada-06-ni	america/managua	11.92988	-85.95602	110219
chinandega-03-ni	america/managua	12.62937	-87.13105	232211
leon-08-ni	america/managua	12.43787	-86.87804	194289
rotterdam-11-nl	europe/amsterdam	51.9225	4.47917	2966998
nijmegen-03-nl	europe/amsterdam	51.8425	5.85278	1138075
harderwijk-03-nl	europe/amsterdam	52.34167	5.62083	211952
assen-01-nl	europe/amsterdam	52.99667	6.5625	240083
eindhoven-06-nl	europe/amsterdam	51.44083	5.47778	1414077
breda-06-nl	europe/amsterdam	51.58656	4.77596	473512
amsterdam-07-nl	europe/amsterdam	52.37403	4.88969	2329291
groningen-04-nl	europe/amsterdam	53.21917	6.56667	370719
almere stad-16-nl	europe/amsterdam	52.37025	5.21413	321955
leeuwarden-02-nl	europe/amsterdam	53.20139	5.80859	253485
utrecht-09-nl	europe/amsterdam	52.09083	5.12222	1041757
enschede-15-nl	europe/amsterdam	52.21833	6.89583	527219
zwolle-15-nl	europe/amsterdam	52.5125	6.09444	317594
maastricht-05-nl	europe/amsterdam	50.84833	5.68889	627619
venlo-05-nl	europe/amsterdam	51.37	6.16806	168282
middelburg-10-nl	europe/amsterdam	51.5	3.61389	201077
fredrikstad-13-no	europe/oslo	59.2181	10.9298	181381
oslo-12-no	europe/oslo	59.91273	10.74609	580000
sandefjord-20-no	europe/oslo	59.13118	10.21665	122341
bergen-07-no	europe/oslo	60.39299	5.32415	254853
drammen-04-no	europe/oslo	59.74389	10.20449	108389
trondheim-16-no	europe/oslo	63.43049	10.39506	147139
stavanger-14-no	europe/oslo	58.97005	5.73332	184642
rishon leziyyon-02-il	asia/jerusalem	31.96417	34.80444	1109595
nazareth-03-il	asia/jerusalem	32.69925	35.30483	535863
ashdod-01-il	asia/jerusalem	31.81667	34.65	422893
beersheba-01-il	asia/jerusalem	31.25181	34.7913	244469
jerusalem-06-il	asia/jerusalem	31.76904	35.21633	1244367
haifa-04-il	asia/jerusalem	32.81841	34.9885	586982
tel aviv-05-il	asia/jerusalem	32.08088	34.78057	1134563
windhoek-21-na	africa/windhoek	-22.55941	17.08323	268132
noumea-02-nc	pacific/noumea	-22.27631	166.4572	112406
zinder-07-ne	africa/niamey	13.80716	8.9881	212148
maradi-04-ne	africa/niamey	13.5	7.10174	183506
niamey-08-ne	africa/niamey	13.51366	2.1098	774235
ilorin-30-ng	africa/lagos	8.5	4.55	814192
benin city-37-ng	africa/lagos	6.33504	5.62749	1125058
auchi-37-ng	africa/lagos	7.06667	6.26667	144307
warri-36-ng	africa/lagos	5.51667	5.75	794105
jos-49-ng	africa/lagos	9.91667	8.9	816824
abakaliki-53-ng	africa/lagos	6.31625	8.11691	378451
katsina-24-ng	africa/lagos	12.98943	7.60063	432149
funtua-24-ng	africa/lagos	11.52325	7.30813	207520
onitsha-25-ng	africa/lagos	6.14543	6.78845	1470810
makurdi-26-ng	africa/lagos	7.7411	8.5121	310311
maiduguri-27-ng	africa/lagos	11.84644	13.16027	1131812
bama-27-ng	africa/lagos	11.5221	13.68558	133297
gambaru-27-ng	africa/lagos	12.37066	14.21731	100379
ikot ekpene-21-ng	africa/lagos	5.17938	7.71082	291164
esuk oron-21-ng	africa/lagos	4.80293	8.25341	137602
akure-48-ng	africa/lagos	7.25256	5.19312	783636
kaduna-23-ng	africa/lagos	10.52224	7.43828	1582102
zaria-23-ng	africa/lagos	11.11128	7.7227	990868
bauchi-46-ng	africa/lagos	10.31344	9.84327	316149
azare-46-ng	africa/lagos	11.6765	10.1948	105687
enugu-47-ng	africa/lagos	6.4402	7.4943	967575
damaturu-44-ng	africa/lagos	11.747	11.9608	255895
gashua-44-ng	africa/lagos	12.871	11.0482	125817
nguru-44-ng	africa/lagos	12.8791	10.4526	127571
potiskum-44-ng	africa/lagos	11.7091	11.0694	164279
aba-45-ng	africa/lagos	5.10658	7.36667	1162222
amaigbo-45-ng	africa/lagos	5.78917	7.83829	280273
ilesa-42-ng	africa/lagos	7.61667	4.73333	277904
kano-29-ng	africa/lagos	12.00012	8.51672	3649134
birnin kebbi-40-ng	africa/lagos	12.45389	4.1975	227243
ogaminan-41-ng	africa/lagos	7.59464	6.22476	149386
owerri-28-ng	africa/lagos	5.48333	7.03041	299650
okigwi-28-ng	africa/lagos	5.83523	7.35989	115499
lafia-56-ng	africa/lagos	8.48333	8.51667	127236
keffi-56-ng	africa/lagos	8.84861	7.87361	116860
jalingo-43-ng	africa/lagos	8.88333	11.36667	117757
effon alaiye-00-ng	africa/lagos	7.65	4.91667	797666
ondo-00-ng	africa/lagos	7.1	4.83333	257005
iwo-00-ng	africa/lagos	7.63333	4.18333	1400012
jimeta-00-ng	africa/lagos	9.28333	12.46667	248148
bida-00-ng	africa/lagos	9.08333	6.01667	199941
kishi-00-ng	africa/lagos	9.08333	3.85	292274
offa-00-ng	africa/lagos	8.15	4.71667	113830
uromi-00-ng	africa/lagos	6.7	6.33333	108608
lafiagi-00-ng	africa/lagos	8.86667	5.41667	102779
wukari-00-ng	africa/lagos	7.85	9.78333	115690
igbo ora-00-ng	africa/lagos	7.43333	3.28333	163746
abuja-11-ng	africa/lagos	9.06853	7.48375	590400
hadejia-39-ng	africa/lagos	12.4498	10.0444	110753
calabar-22-ng	africa/lagos	4.9517	8.322	461796
ugep-22-ng	africa/lagos	5.8086	8.0812	200276
abeokuta-16-ng	africa/lagos	7.15	3.35	958864
ijebu ode-16-ng	africa/lagos	6.81609	3.91588	318436
gombe-55-ng	africa/lagos	10.28969	11.16729	447080
ibadan-32-ng	africa/lagos	7.38778	3.89639	3636569
oyo-32-ng	africa/lagos	7.85	3.93333	736072
saki-32-ng	africa/lagos	8.66667	3.38333	178677
minna-31-ng	africa/lagos	9.61389	6.55694	316352
suleja-31-ng	africa/lagos	9.18052	7.17933	162135
kontagora-31-ng	africa/lagos	10.39989	5.46949	114319
lagos-05-ng	africa/lagos	6.45306	3.39583	9313439
sokoto-51-ng	africa/lagos	13.06092	5.23902	581347
port harcourt-50-ng	africa/lagos	4.77742	7.0134	1542635
mubi-35-ng	africa/lagos	10.26761	13.26436	225705
ise ekiti-54-ng	africa/lagos	7.4632	5.4281	545165
ijero ekiti-54-ng	africa/lagos	7.8139	5.0742	324236
gusau-57-ng	africa/lagos	12.16278	6.66135	296582
lower hutt-g2046-nz	pacific/auckland	-41.21667	174.91667	101194
wellington-g2047-nz	pacific/auckland	-41.28664	174.77557	381900
dunedin-f7071-nz	pacific/auckland	-45.87416	170.50361	114347
auckland-e7076-nz	pacific/auckland	-36.86667	174.76667	1279151
hamilton-g1016-nz	pacific/auckland	-37.78333	175.28333	152641
christchurch-e9060-nz	pacific/auckland	-43.53333	172.63333	363926
tauranga-e8023-nz	pacific/auckland	-37.68611	176.16667	110338
patan-00-np	asia/kathmandu	27.67658	85.31417	357472
birganj-00-np	asia/kathmandu	27.01043	84.87735	160563
dharan bazar-00-np	asia/kathmandu	26.81248	87.28355	156584
bharatpur-00-np	asia/kathmandu	27.68333	84.43333	107157
janakpur-00-np	asia/kathmandu	26.71828	85.90646	162281
dhangarhi-00-np	asia/kathmandu	28.70792	80.59611	180675
butwal-00-np	asia/kathmandu	27.70055	83.44836	137293
biratnagar-er07-np	asia/kathmandu	26.4831	87.28337	182324
pokhara-wr04-np	asia/kathmandu	28.26689	83.96851	200000
kathmandu-cr01-np	asia/kathmandu	27.70169	85.3206	1442271
as salimiyah-00-kw	asia/kuwait	29.33389	48.07611	586328
ar riqqah-04-kw	asia/kuwait	29.14583	48.09472	114164
mulhouse-c168-fr	europe/paris	47.75	7.33333	228910
strasbourg-c167-fr	europe/paris	48.58342	7.74296	426775
poitiers-b786-fr	europe/paris	46.58333	0.33333	123170
nantes-b544-fr	europe/paris	47.21725	-1.55336	580793
angers-b549-fr	europe/paris	47.46667	-0.55	201508
lorient-a256-fr	europe/paris	47.75	-3.36667	173888
beauvais-b660-fr	europe/paris	49.43333	2.08333	124106
calais-b462-fr	europe/paris	50.9581	1.85205	155344
arras-b462-fr	europe/paris	50.29301	2.78186	238131
limoges-b187-fr	europe/paris	45.83153	1.2578	141176
evry-a891-fr	europe/paris	48.63333	2.45	692434
evreux-a727-fr	europe/paris	49.02414	1.15082	103052
le mans-b572-fr	europe/paris	48.0	0.2	163051
reims-a451-fr	europe/paris	49.25	4.03333	274904
dijon-a121-fr	europe/paris	47.31667	5.01667	189735
chartres-a328-fr	europe/paris	48.44685	1.48925	108682
meaux-a877-fr	europe/paris	48.96014	2.87885	459829
paris-a875-fr	europe/paris	48.85341	2.3488	2138551
nice-b806-fr	europe/paris	43.70313	7.26608	766265
versailles-a878-fr	europe/paris	48.8	2.13333	907724
toulon-b883-fr	europe/paris	43.11667	5.93333	435011
frejus-b883-fr	europe/paris	43.43286	6.73524	126589
avignon-b884-fr	europe/paris	43.94834	4.80892	254833
perpignan-a966-fr	europe/paris	42.69764	2.89541	110706
caen-9914-fr	europe/paris	49.18585	-0.35912	175318
amiens-b680-fr	europe/paris	49.9	2.3	169547
rennes-a235-fr	europe/paris	48.11198	-1.67429	266582
grenoble-b938-fr	europe/paris	45.16667	5.71667	310041
vienne-b938-fr	europe/paris	45.51667	4.86667	100349
tours-a337-fr	europe/paris	47.38333	0.68333	227715
besancon-a625-fr	europe/paris	47.24878	6.01815	148739
lille-b459-fr	europe/paris	50.63297	3.05858	1015614
dunkerque-b459-fr	europe/paris	51.05	2.36667	143336
orleans-a345-fr	europe/paris	47.90289	1.90389	221477
brest-a229-fr	europe/paris	48.4	-4.48333	177541
valence-b926-fr	europe/paris	44.93333	4.9	154273
bordeaux-9733-fr	europe/paris	44.84044	-0.5805	695384
creteil-a894-fr	europe/paris	48.78333	2.46667	1205446
argenteuil-a895-fr	europe/paris	48.95	2.25	811584
saint etienne-b942-fr	europe/paris	45.43333	4.4	248360
boulogne billancourt-a892-fr	europe/paris	48.83333	2.25	1500957
saint denis-a893-fr	europe/paris	48.93333	2.36667	1370017
la roche sur yon-b585-fr	europe/paris	46.66667	-1.43333	110126
marseille-b813-fr	europe/paris	43.29695	5.38107	1345413
chambery-b973-fr	europe/paris	45.56667	5.93333	108404
la rochelle-b717-fr	europe/paris	46.16667	-1.15	106237
annecy-b974-fr	europe/paris	45.9	6.11667	173486
toulouse-b331-fr	europe/paris	43.60426	1.44367	591565
clermont ferrand-9863-fr	europe/paris	45.77966	3.08628	213953
le havre-a776-fr	europe/paris	49.4938	0.10767	224681
rouen-a776-fr	europe/paris	49.44313	1.09932	336115
chalon sur saone-a171-fr	europe/paris	46.78333	4.85	140623
nimes-a930-fr	europe/paris	43.83333	4.35	210286
montpellier-a934-fr	europe/paris	43.61092	3.87723	414549
bayonne-9764-fr	europe/paris	43.48333	-1.48333	118242
metz-b257-fr	europe/paris	49.11911	6.17269	244035
nancy-b254-fr	europe/paris	48.68333	6.2	224014
lyon-b969-fr	europe/paris	45.74846	4.84671	1074713
hameenlinna-1305-fi	europe/helsinki	60.99596	24.46434	107262
lahti-1307-fi	europe/helsinki	60.98267	25.66151	140080
helsinki-1301-fi	europe/helsinki	60.16952	24.93545	1281117
oulu-0817-fi	europe/helsinki	65.01236	25.46816	145916
kotka-1308-fi	europe/helsinki	60.46667	26.91667	147107
turku-1502-fi	europe/helsinki	60.45148	22.26869	276882
tampere-1506-fi	europe/helsinki	61.49911	23.78712	331881
pori-1504-fi	europe/helsinki	61.48333	21.78333	113322
kuopio-1411-fi	europe/helsinki	62.89238	27.67703	109313
jyvaeskylae-1513-fi	europe/helsinki	62.23333	25.73333	117380
kulob-02-tj	asia/dushanbe	37.91458	69.78454	142909
khujand-03-tj	asia/dushanbe	40.28256	69.62216	182843
dushanbe-7280679-tj	asia/dushanbe	38.53575	68.77905	543107
manzini-03-sz	africa/mbabane	-26.48333	31.36667	110537
homs-11-sy	asia/damascus	34.72682	36.72339	959682
hamah-10-sy	asia/damascus	35.13179	36.75783	692974
damascus-13-sy	asia/damascus	33.5102	36.29128	1569394
idlib-12-sy	asia/damascus	35.93062	36.63393	365684
tafas-06-sy	asia/damascus	32.73564	36.06694	166014
dayr az zawr-07-sy	asia/damascus	35.33588	40.14084	297099
ar raqqah-04-sy	asia/damascus	35.95283	39.00788	265516
latakia-02-sy	asia/damascus	35.51484	35.77684	406096
douma-08-sy	asia/damascus	33.57175	36.4027	479401
aleppo-09-sy	asia/damascus	36.20124	37.16117	2058451
tartouss-14-sy	asia/damascus	34.88902	35.88659	156338
jalal abad-03-kg	asia/bishkek	40.93333	73.0	103404
bishkek-01-kg	asia/bishkek	42.87	74.59	900000
osh-08-kg	asia/bishkek	40.51506	72.80826	217800
mombasa-02-ke	africa/nairobi	-4.05466	39.66359	799668
thika-01-ke	africa/nairobi	-1.03326	37.06933	142032
kisumu-07-ke	africa/nairobi	-0.10221	34.76171	231696
nairobi-05-ke	africa/nairobi	-1.28333	36.81667	2750547
nakuru-08-ke	africa/nairobi	-0.28333	36.06667	318270
eldoret-08-ke	africa/nairobi	0.52036	35.26992	218446
kakamega-09-ke	africa/nairobi	0.28422	34.75228	187380
juba-01-ss	africa/juba	4.85165	31.58247	300000
malakal-07-ss	africa/juba	9.53342	31.66048	160765
wau-09-ss	africa/juba	7.70286	27.9953	127384
paramaribo-16-sr	america/paramaribo	5.86638	-55.16682	223757
siemreab-24-kh	asia/phnom_penh	13.36179	103.86056	139458
paoy pet-25-kh	asia/phnom_penh	13.65611	102.5625	102218
phnom penh-22-kh	asia/phnom_penh	11.56245	104.91601	1573544
sihanoukville-28-kh	asia/phnom_penh	10.60932	103.52958	156691
batdambang-29-kh	asia/phnom_penh	13.10271	103.19822	150444
santa ana-11-sv	america/el_salvador	13.99417	-89.55972	228086
san salvador-10-sv	america/el_salvador	13.68935	-89.18718	1384512
sonsonate-13-sv	america/el_salvador	13.71889	-89.72417	116874
santa tecla-05-sv	america/el_salvador	13.67694	-89.27972	204202
san miquel-09-sv	america/el_salvador	13.48333	-88.18333	180975
bratislava-02-sk	europe/bratislava	48.14816	17.10674	462853
kosice-03-sk	europe/bratislava	48.71395	21.25808	299870
nove zamky-00-sk	europe/bratislava	47.98544	18.16195	119413
banska bystrica-01-sk	europe/bratislava	48.73946	19.15349	184305
trencin-06-sk	europe/bratislava	48.89452	18.04436	102214
trnava-07-sk	europe/bratislava	48.3774	17.58723	145456
nitra-04-sk	europe/bratislava	48.30763	18.08453	209732
prievidza-04-sk	europe/bratislava	48.77446	18.6275	116455
presov-05-sk	europe/bratislava	48.99839	21.23393	152173
zilina-08-sk	europe/bratislava	49.22315	18.73941	241848
seoul-11-kr	asia/seoul	37.56826	126.97783	10349312
busan-10-kr	asia/seoul	35.10278	129.04028	3721619
suigen-13-kr	asia/seoul	37.29111	127.00889	7594101
vijongbu-13-kr	asia/seoul	37.7415	127.0474	757687
incheon-12-kr	asia/seoul	37.45361	126.73167	2653535
daegu-15-kr	asia/seoul	35.87028	128.59111	2631258
ulsan-21-kr	asia/seoul	35.53722	129.31667	962865
tenan-17-kr	asia/seoul	36.8065	127.1522	674709
suisan-17-kr	asia/seoul	36.78167	126.45222	159396
nonsan-17-kr	asia/seoul	36.20389	127.08472	126745
jeonju-03-kr	asia/seoul	35.82194	127.14889	1484751
daejeon-19-kr	asia/seoul	36.32139	127.41972	1475221
gwangju-18-kr	asia/seoul	35.15472	126.91556	1416938
cheongju-05-kr	asia/seoul	36.63722	127.48972	796655
reisui-16-kr	asia/seoul	34.74417	127.73778	681913
moppo-16-kr	asia/seoul	34.79361	126.38861	387939
hwasun-16-kr	asia/seoul	35.05944	126.985	109823
jeju-01-kr	asia/seoul	33.50972	126.52194	432081
wonju-06-kr	asia/seoul	37.35139	127.94528	344051
chuncheon-06-kr	asia/seoul	37.87472	127.73417	257595
kang neung-06-kr	asia/seoul	37.75556	128.89611	323884
sogcho-06-kr	asia/seoul	38.20833	128.59111	151493
changwon-20-kr	asia/seoul	35.22806	128.68111	1936279
chinju-20-kr	asia/seoul	35.19278	128.08472	307242
hoko-14-kr	asia/seoul	36.03222	129.365	788175
kumi-14-kr	asia/seoul	36.1136	128.336	751629
andong-14-kr	asia/seoul	36.56556	128.725	326782
ljubljana-61-si	europe/ljubljana	46.05108	14.50513	255115
sinuiju-11-kp	asia/pyongyang	40.10056	124.39806	338193
hamhung-03-kp	asia/pyongyang	39.91833	127.53639	1016968
hyesan dong-13-kp	asia/pyongyang	41.39756	128.17873	118200
pyongyang-12-kp	asia/pyongyang	39.03385	125.75432	3346780
kaesong-06-kp	asia/pyongyang	37.97083	126.55444	360820
haeju-06-kp	asia/pyongyang	38.04056	125.71472	356077
sariwon-07-kp	asia/pyongyang	38.50722	125.75583	388440
ch'ongjin-17-kp	asia/pyongyang	41.79556	129.77583	396659
wonsan-09-kp	asia/pyongyang	39.15278	127.44361	406449
kanggye si-01-kp	asia/pyongyang	40.96946	126.58523	209530
namp'o-15-kp	asia/pyongyang	38.7375	125.40778	455000
mogadishu-02-so	africa/mogadishu	2.03711	45.34375	2587183
hargeysa-20-so	africa/mogadishu	9.56	44.065	477876
berbera-20-so	africa/mogadishu	10.43959	45.01432	242344
baydhabo-04-so	africa/mogadishu	3.11383	43.6498	129839
kismaayo-09-so	africa/mogadishu	-0.35817	42.54536	234852
jamaame-09-so	africa/mogadishu	0.06968	42.74497	185270
touba-03-sn	africa/dakar	14.85	-15.88333	703565
ziguinchor-12-sn	africa/dakar	12.58333	-16.27194	186015
thies nones-07-sn	africa/dakar	14.78333	-16.96667	305150
kaolack-10-sn	africa/dakar	14.1825	-16.25333	172305
dakar-01-sn	africa/dakar	14.6937	-17.44406	5702519
saint louis-14-sn	africa/dakar	16.01793	-16.48962	176000
bo-03-sl	africa/freetown	7.96472	-11.73833	174354
kenema-01-sl	africa/freetown	7.87667	-11.1875	143137
freetown-04-sl	africa/freetown	8.484	-13.22994	822389
almaty-02-kz	asia/almaty	43.25654	76.92848	2000900
shymkent-10-kz	asia/almaty	42.3	69.6	461385
turkestan-10-kz	asia/almaty	43.33333	68.25	154768
qostanay-13-kz	asia/qyzylorda	53.21435	63.62463	334000
karagandy-12-kz	asia/almaty	49.83333	73.1658	700406
zhezqazghan-12-kz	asia/almaty	47.78333	67.76667	104357
ust' kamenogorsk-15-kz	asia/almaty	49.96466	82.60898	319067
semey-15-kz	asia/almaty	50.42675	80.26669	292780
qyzylorda-14-kz	asia/qyzylorda	44.85278	65.50917	316455
taraz-17-kz	asia/almaty	42.9	71.36667	373285
astana-05-kz	asia/almaty	51.1801	71.44598	345604
petropavlovsk-16-kz	asia/almaty	54.87278	69.143	200920
kokshetau-16-kz	asia/almaty	53.28244	69.39692	124444
taldyqorghan-00-kz	asia/almaty	45.0	77.91667	200000
taldyqorghan-01-kz	asia/almaty	45.01556	78.37389	163728
talghar-01-kz	asia/almaty	43.30348	77.24085	115049
aktau-09-kz	asia/aqtau	43.64806	51.17222	147443
oral-07-kz	asia/oral	51.23333	51.36667	200000
pavlodar-11-kz	asia/almaty	52.27401	77.00438	373810
ekibastuz-11-kz	asia/almaty	51.72371	75.32287	121470
atyrau-06-kz	asia/oral	47.11667	51.88333	199260
aqtobe-04-kz	asia/aqtobe	50.27969	57.20718	262457
abha-11-sa	asia/riyadh	18.21639	42.50528	210886
riyadh-10-sa	asia/riyadh	24.68773	46.72185	4205961
khamis mushayt-00-sa	asia/riyadh	18.30639	42.72917	387553
najran-00-sa	asia/riyadh	17.4924	44.12766	258573
al qatif-00-sa	asia/riyadh	26.5208	50.02452	183630
ad dammam-06-sa	asia/riyadh	26.43442	50.10326	1187707
al hufuf-06-sa	asia/riyadh	25.36457	49.56532	638269
al jubayl-06-sa	asia/riyadh	27.01122	49.65826	237274
jeddah-14-sa	asia/riyadh	21.51694	39.21917	2867446
mecca-14-sa	asia/riyadh	21.42667	39.82611	1345831
ta'if-14-sa	asia/riyadh	21.27028	40.41583	530848
jizan-17-sa	asia/riyadh	16.88917	42.55111	208477
medina-05-sa	asia/riyadh	24.46861	39.61417	2246697
yanbu` al bahr-05-sa	asia/riyadh	24.08912	38.06374	200161
tabuk-19-sa	asia/riyadh	28.38333	36.58333	455450
buraydah-08-sa	asia/riyadh	26.32599	43.97497	555065
hayil-13-sa	asia/riyadh	27.52188	41.69073	267005
sakaka-20-sa	asia/riyadh	29.96974	40.20641	128332
al qurayyat-20-sa	asia/riyadh	31.33176	37.34282	102903
`ar`ar-15-sa	asia/riyadh	30.97531	41.03808	148540
singapore-00-sg	asia/singapore	1.28967	103.85007	3547809
vasteras-25-se	europe/stockholm	59.61617	16.55276	123811
stockholm-26-se	europe/stockholm	59.33258	18.0649	2210439
malmoe-27-se	europe/stockholm	55.60587	13.00073	407092
helsingborg-27-se	europe/stockholm	56.04673	12.69437	113410
orebro-15-se	europe/stockholm	59.27412	15.2066	125522
uppsala-21-se	europe/stockholm	59.8585	17.64543	147467
linkoping-16-se	europe/stockholm	58.41086	15.62157	209350
jonkoping-08-se	europe/stockholm	57.78145	14.15618	120656
goeteborg-28-se	europe/stockholm	57.70716	11.96679	683453
wad medani-38-sd	africa/khartoum	14.40118	33.51989	361449
al manaqil-38-sd	africa/khartoum	14.2459	32.9891	128297
sinnar-58-sd	africa/khartoum	13.56907	33.56718	192373
el fasher-55-sd	africa/khartoum	13.62793	25.34936	252609
el geneina-47-sd	africa/khartoum	13.45262	22.44725	162981
el obeid-56-sd	africa/khartoum	13.18421	30.21669	393311
an nuhud-56-sd	africa/khartoum	12.7	28.43333	108008
ad damazin-42-sd	africa/khartoum	11.7891	34.3592	214913
khartoum-29-sd	africa/khartoum	15.55177	32.53241	3174647
atbara-53-sd	africa/khartoum	17.70217	33.98638	234266
kosti-41-sd	africa/khartoum	13.1629	32.66347	480349
port sudan-36-sd	africa/khartoum	19.61745	37.21644	489725
kassala-52-sd	africa/khartoum	15.45099	36.39998	401477
    """
    city_info = dict()
    counter = 0
    for l in city_collapsed_all.split("\n"):
        segs = l.lower().split('\t')
        if len(segs) != 5:
            continue
        name, tz, lat, lon, population = segs
        city_info[name] = (float(lat), float(lon), counter)
        counter += 1
    #print counter
    return city_info

def round_prec(num):
    """    round coordinates to appropriate grid size    """
    fraction, integer = math.modf(num)
    if fraction >= 0.5:
        fraction = 0.5
    else:
        fraction = 0
    return integer + fraction

def build_city_grids(city_info_dict):
    """    map cities into grid_size specified cells    """
    city_grids = dict()
    for city_name in city_info_dict:
        lat, lon, counter = city_info_dict[city_name]
        key = "{0},{1}".format(round_prec(lat), round_prec(lon))
        rec = (city_name, lat, lon)
        try:
            city_grids[key].append(rec)
        except KeyError:
            city_grids[key] = [rec]
    #print "city grid number is :{0}".format(len(city_grids))
    return city_grids
    
def zoom_search(lat, lon):
    """    search the nearest city by lat and lon    """
    # generate search areas, nine blocks search
    grid_lat = round_prec(lat)
    lats = [grid_lat - grid_size, grid_lat, grid_lat + grid_size]
    grid_lon = round_prec(lon)
    lons = [grid_lon - grid_size, grid_lon, grid_lon + grid_size]
    keys = itertools.product(lats, lons)

    # find the most suitable key
    results = []
    for key in keys:
        klat, klon = key
        city_key = "{0},{1}".format(klat, klon)
        try:
            city_list = city_grids[city_key]
        except KeyError:
            continue 
        for city in city_list:
            name, clat, clon = city
            gcd_error_distance = calc_dist_degree(clat, clon, lat, lon)
            results.append((name, gcd_error_distance))
    if len(results) > 0:
        sorted_results = sorted(results, key = lambda k:k[1])
        return sorted_results[0]
    else:
        return (None, None)

def lookup_city(lat, lon):
    city, offset_distance = zoom_search(lat, lon)
    if city:
        return city
    else:
        return None

def lookup_coords(city):
    if city in city_info:
        lat, lon = city_info[city][:2]
        return lat, lon
    else:
        return None
    
city_info = load_city_info()
city_grids = build_city_grids(city_info)

if __name__ == "__main__":
    print zoom_search(44.86503177,-85.51900375)
    print zoom_search(54.64403, -2.69027)
    print zoom_search(53.76667, -2.71667)
    print calc_dist_degree(54.64403, -2.69027, 53.76667, -2.71667)
    print zoom_search(4.77742, 7.0134)
    print zoom_search(45.547761,-122.591969)
