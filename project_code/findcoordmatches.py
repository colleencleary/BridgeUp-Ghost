# ===============================================
# import libraries
# ===============================================
import pandas as pd
from astrodbkit import astrodb
import astropy.coordinates as coord
from astropy.coordinates import SkyCoord
import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np




# ===============================================
# function definitions
# ===============================================

def matches_sortCSV(gaia_catalogue, db, save=False):
    # ===============================================
    # create new empty dataframes to store gaia data
    # ===============================================

    # matches will store gaia data for objects in BDNYC database
    matches = pd.DataFrame(columns=np.insert(gaia_catalogue.columns.values, 0, 'source_id', axis=0))

    # new_objects will store gaia data for objects that do not exist in BDNYC database
    new_objects = pd.DataFrame(columns=gaia_catalogue.columns.values)
    # needs_review will store gaia data for objects that have too many matched in the database and need further review
    needs_review = pd.DataFrame(columns=gaia_catalogue.columns.values)

    # ===============================================
    # sort each row of gaia data into matches/new_objects using celestial coordinates: right ascension (ra/RA) and declination (dec/DEC)
    # ===============================================
    for i in range(len(gaia_catalogue)):
        results=db.search((gaia_catalogue['RA'][i], gaia_catalogue['DEC'][i]), 'sources', radius=0.00278, fetch=True)

        if len(results) == 1:
            matches = matches.append(gaia_catalogue.loc[[i]])
            matches['source_id'].loc[i]=results['id'][0]
        elif len(results)>1:
        # if there is MORE THAN ONE result, just print a note
            needs_review = needs_review.append(gaia_catalogue.loc[[i]])
        else:
            new_objects = new_objects.append(gaia_catalogue.loc[[i]])

    if save==True:
        saveCSVfiles(matches, new_objects, needs_review)

    return matches, new_objects

def saveCSVfiles(matches, new_objects, needs_review):
    matches.to_csv('matches.csv')
    new_objects.to_csv('new_objects.csv')
    needs_review.to_csv('needs_review.csv')
    print('matches, new_objects, and needs_review saved as CSV files.')

def plotCoords(db_sources, matches, new_objects):
    # ===============================================
    # Plotting coordinates
    # ===============================================

    # converting BDNYC database coordinates for plot
    db_ra = coord.Angle(pd.to_numeric(db_sources['ra']).fillna(np.nan).values*u.degree)
    db_ra = db_ra.wrap_at(180*u.degree)
    db_dec = coord.Angle(pd.to_numeric(db_sources['dec']).fillna(np.nan).values*u.degree)

    # converting matches csv coordinates
    matches_ra = coord.Angle(matches['RA'].values*u.degree)
    matches_ra = matches_ra.wrap_at(180*u.degree)
    matches_dec = coord.Angle(matches['DEC'].values*u.degree)

    # converting new_objects csv coordinates
    new_objects_ra = coord.Angle(new_objects['RA'].values*u.degree)
    new_objects_ra = new_objects_ra.wrap_at(180*u.degree)
    new_objects_dec = coord.Angle(new_objects['DEC'].values*u.degree)


    fig = plt.figure(figsize=(14,12))
    ax = fig.add_subplot(111, projection="mollweide")
    ax.set_facecolor('#17303F')
    plt.grid(True)
    ax.scatter(db_ra.radian, db_dec.radian, color="#E5E5E5", alpha=.8, edgecolors='face', label='in BDNYC database')
    ax.scatter(matches_ra.radian, matches_dec.radian, color="#F24333", label='in BDNYC database and GAIA dataset')
    ax.scatter(new_objects_ra.radian, new_objects_dec.radian, color="#E3B505", label='in GAIA dataset')
    ax.legend(loc=4)

def generateMatchtables(matches, addToDb=False):
    ##################################################
    # matches tables
    ##################################################

    # create new empty list to store data we want to add to database
    matchParallax_data = list()
    matchPropermotions_data = list()
    matchPhotometry_data = list()

    # append the column name (as it's written in the BDNYC database) to match on the appropriate column
    matchParallax_data.append(['source_id','parallax', 'parallax_unc','publication_shortname', 'adopted','comments'])
    matchPropermotions_data.append(['source_id','proper_motion_ra', 'proper_motion_ra_unc','proper_motion_dec', 'proper_motion_dec_unc','publication_shortname', 'comments'])
    matchPhotometry_data.append(['source_id','band', 'magnitude','magnitude_unc', 'publication_shortname', 'comments'])



    for i in range(len(matches)):
        matchParallax_data.append([matches.iloc[[i]]['source_id'].values[0], matches.iloc[[i]]['PARALLAX'].values[0], matches.iloc[[i]]['PARALLAX_ERROR'].values[0], 'GaiaDR2', 1, 'added by SpectreCell'])
        matchPropermotions_data.append([matches.iloc[[i]]['source_id'].values[0], matches.iloc[[i]]['PMRA'].values[0], matches.iloc[[i]]['PMRA_ERROR'].values[0], matches.iloc[[i]]['PMDEC'].values[0], matches.iloc[[i]]['PMDEC_ERROR'].values[0],'GaiaDR2','added by SpectreCell'])
        matchPhotometry_data.append([matches.iloc[[i]]['source_id'].values[0], 'GaiaDR2_G', matches.iloc[[i]]['PHOT_G_MEAN_MAG'].values[0], matches.iloc[[i]]['PHOT_G_MEAN_MAG_ERROR'].values[0],'GaiaDR2','added by SpectreCell'])
        matchPhotometry_data.append([matches.iloc[[i]]['source_id'].values[0], 'GaiaDR2_BP', matches.iloc[[i]]['PHOT_BP_MEAN_MAG'].values[0], matches.iloc[[i]]['PHOT_BP_MEAN_MAG_ERROR'].values[0],'GaiaDR2','added by SpectreCell'])
        matchPhotometry_data.append([matches.iloc[[i]]['source_id'].values[0], 'GaiaDR2_RP', matches.iloc[[i]]['PHOT_RP_MEAN_MAG'].values[0], matches.iloc[[i]]['PHOT_RP_MEAN_MAG_ERROR'].values[0],'GaiaDR2','added by SpectreCell'])

    if addToDb==True:
        db.add_data(matchParallax_data, 'parallaxes')
        db.add_data(matchPropermotions_data, 'proper_motions')
        db.add_data(matchPhotometry_data, 'photometry')

    return matchParallax_data, matchPropermotions_data, matchPhotometry_data

def generateNewObjTables(new_objects, db, addSourceTable=False):
    ##################################################
    # new objects tables
    ##################################################

    # create new empty list to store data we want to add to database
    newobjects_data = list()

    # append the column name (as it's written in the BDNYC database) to match on the appropriate column
    newobjects_data.append(['ra','dec', 'designation','publication_shortname', 'shortname','names', 'comments'])

    for i in range(len(new_objects)):
        newobjects_data.append([new_objects.iloc[[i]]['RA'].values[0], new_objects.iloc[[i]]['DEC'].values[0], new_objects.iloc[[i]]['DISCOVERYNAME'].values[0], 'GaiaDR2', new_objects.iloc[[i]]['SHORTNAME'].str.replace('J', '').str.strip().values[0], new_objects.iloc[[i]]['SOURCE_ID'].values[0],'added by SpectreCell'])

    if addSourceTable==True:
        db.add_data(newobjects_data, 'sources')

    # create new empty list to store data we want to add to database
    newObjParallax_data = list()
    newObjPropermotions_data = list()
    newObjPhotometry_data = list()

    # append the column name (as it's written in the BDNYC database) to match on the appropriate column
    newObjParallax_data.append(['source_id','parallax', 'parallax_unc','publication_shortname', 'adopted','comments'])
    newObjPropermotions_data.append(['source_id','proper_motion_ra', 'proper_motion_ra_unc','proper_motion_dec', 'proper_motion_dec_unc','publication_shortname', 'comments'])
    newObjPhotometry_data.append(['source_id','band', 'magnitude','magnitude_unc', 'publication_shortname', 'comments'])

    for i in range(len(new_objects)):
        db_sourceid=db.search((new_objects['RA'].iloc[[i]], new_objects['DEC'].iloc[[i]]), 'sources', radius=0.00278, fetch=True)['id'][0]

        newObjParallax_data.append([db_sourceid, new_objects.iloc[[i]]['PARALLAX'].values[0], new_objects.iloc[[i]]['PARALLAX_ERROR'].values[0], 'GaiaDR2', 1, 'added by SpectreCell'])

        newObjPropermotions_data.append([db_sourceid, new_objects.iloc[[i]]['PMRA'].values[0], new_objects.iloc[[i]]['PMRA_ERROR'].values[0], new_objects.iloc[[i]]['PMDEC'].values[0], new_objects.iloc[[i]]['PMDEC_ERROR'].values[0],'GaiaDR2','added by SpectreCell'])

        newObjPhotometry_data.append([db_sourceid, 'GaiaDR2_G', new_objects.iloc[[i]]['PHOT_G_MEAN_MAG'].values[0], new_objects.iloc[[i]]['PHOT_G_MEAN_MAG_ERROR'].values[0],'GaiaDR2','added by SpectreCell'])
        newObjPhotometry_data.append([db_sourceid, 'GaiaDR2_BP', new_objects.iloc[[i]]['PHOT_BP_MEAN_MAG'].values[0], new_objects.iloc[[i]]['PHOT_BP_MEAN_MAG_ERROR'].values[0],'GaiaDR2','added by SpectreCell'])
        newObjPhotometry_data.append([db_sourceid, 'GaiaDR2_RP', new_objects.iloc[[i]]['PHOT_RP_MEAN_MAG'].values[0], new_objects.iloc[[i]]['PHOT_RP_MEAN_MAG_ERROR'].values[0],'GaiaDR2','added by SpectreCell'])
        newObjPhotometry_data.append([db_sourceid, '2MASS_J', new_objects.iloc[[i]]['TMASSJ'].values[0], new_objects.iloc[[i]]['TMASSJERR'].values[0],'GaiaDR2','added by SpectreCell'])
        newObjPhotometry_data.append([db_sourceid, '2MASS_H', new_objects.iloc[[i]]['TMASSH'].values[0], new_objects.iloc[[i]]['TMASSHERR'].values[0],'GaiaDR2','added by SpectreCell'])
        newObjPhotometry_data.append([db_sourceid, '2MASS_K', new_objects.iloc[[i]]['TMASSK'].values[0], new_objects.iloc[[i]]['TMASSKERR'].values[0],'GaiaDR2','added by SpectreCell'])

        newObjPhotometry_data.append([db_sourceid, 'WISE_W1', new_objects.iloc[[i]]['WISEW1'].values[0], new_objects.iloc[[i]]['WISEW1ERR'].values[0],'GaiaDR2','added by SpectreCell'])
        newObjPhotometry_data.append([db_sourceid, 'WISE_W2', new_objects.iloc[[i]]['WISEW2'].values[0], new_objects.iloc[[i]]['WISEW2ERR'].values[0],'GaiaDR2','added by SpectreCell'])
        newObjPhotometry_data.append([db_sourceid, 'WISE_W3', new_objects.iloc[[i]]['WISEW3'].values[0], new_objects.iloc[[i]]['WISEW3ERR'].values[0],'GaiaDR2','added by SpectreCell'])

        newObjPhotometry_data.append([db_sourceid, 'GUNN_G', new_objects.iloc[[i]]['GUNNG'].values[0], new_objects.iloc[[i]]['GUNNGERR'].values[0],'GaiaDR2','added by SpectreCell'])
        newObjPhotometry_data.append([db_sourceid, 'GUNN_R', new_objects.iloc[[i]]['GUNNR'].values[0], new_objects.iloc[[i]]['GUNNRERR'].values[0],'GaiaDR2','added by SpectreCell'])
        newObjPhotometry_data.append([db_sourceid, 'GUNN_I', new_objects.iloc[[i]]['GUNNI'].values[0], new_objects.iloc[[i]]['GUNNIERR'].values[0],'GaiaDR2','added by SpectreCell'])
        newObjPhotometry_data.append([db_sourceid, 'GUNN_Z', new_objects.iloc[[i]]['GUNNZ'].values[0], new_objects.iloc[[i]]['GUNNZERR'].values[0],'GaiaDR2','added by SpectreCell'])
        newObjPhotometry_data.append([db_sourceid, 'GUNN_Y', new_objects.iloc[[i]]['GUNNY'].values[0], new_objects.iloc[[i]]['GUNNYERR'].values[0],'GaiaDR2','added by SpectreCell'])

    return newObjParallax_data, newObjPropermotions_data, newObjPhotometry_data




##################################################
# CODE STARTS HERE
##################################################


# ===============================================
# import files needed
# ===============================================

# import gaia csv
gaia_catalogue = pd.read_csv('GUCDScat.csv')
# import bdnyc database
db = astrodb.Database('BDNYCdb_practice/bdnycdev_copy.db')

# load matches and new_objects csvs
matches = pd.read_csv('matches.csv', index_col=0)
new_objects = pd.read_csv('new_objects.csv', index_col=0)



# ===============================================
# sort data into matches and not matches and save as new csv files
# ===============================================

# matches, new_objects = matches_sortCSV(gaia_catalogue, db, save=True)


# ===============================================
# Workspace
# ===============================================

matchParallax_data, matchPropermotions_data, matchPhotometry_data = generateMatchtables(matches)

len(newObjPhotometry_data)

newObjParallax_data, newObjPropermotions_data, newObjPhotometry_data = generateNewObjTables(new_objects, db)



new_objects['SPTNIRNAME'].unique()




newObjSpecTypes=new_objects['SPTNIRNAME'].str.strip().str.replace(' ','').str.replace('M', '').str.replace('L', '1').str.replace('T', '2').str.replace('Y', '3').dropna()

st = list()
st.append(['source_id', 'spectral_type', 'gravity', 'suffix', 'regime', 'comments'])

specnotes=db.query('SELECT gravity, suffix from spectral_types', fmt='pandas')

specnotes


gravitylist=list(specnotes['gravity'].unique())
suffixlist.remove(None)
gravitylist.sort(key=len, reverse=True)

suffixlist=list(specnotes['suffix'].unique())
gravitylist
suffixlist.sort(key=len, reverse=True)
suffixlist

newObjSpecTypes[pd.notna(newObjSpecTypes)].index
new_objects['SPTNIRNAME']
for i in newObjSpecTypes[pd.notna(newObjSpecTypes)].index:
    if newObjSpecTypes[i].strip()!='...' and '-999' not in newObjSpecTypes[i]:
        i=3
        gravity=''
        suffix=''
        comment='added by SpectreCell: '+new_objects['SPTNIRNAME'][i]

        newObjSpecTypes[i]=newObjSpecTypes[i].replace('(', '').replace(')', '').replace('?', '').replace(' ', '')

        for s in suffixlist:
            if str(s) in newObjSpecTypes[i]:
                suffix+=str(s)
                if str(s) in gravitylist:
                    gravity+=str(s)
                newObjSpecTypes[i]=newObjSpecTypes[i].replace(str(s), '')

        for g in gravitylist:
            if str(g) in newObjSpecTypes[i]:
                gravity+=str(g)
                newObjSpecTypes[i]=newObjSpecTypes[i].replace(str(g), '').replace('amma', '')
        gravity
        suffix
        if '+' in newObjSpecTypes[i]:
            st.append([0, newObjSpecTypes[i], gravity, suffix, 'NIR', comment])
        elif '+' not in newObjSpecTypes:
            st.append([0, float(newObjSpecTypes[i]), gravity, suffix, 'NIR', comment])
        else:
            print([0, newObjSpecTypes[i], gravity, suffix, 'NIR', comment])

st


stdf=pd.DataFrame(st, columns=st[0])
stdf[100:200]
new_objects['SPTNIRNAME'].sort_values().unique()

if ':' in new_objects['SPTNIRNAME'][i]:
    suffix+=
    for spectype in new_objects['SPTNIRNAME'][i].strip(":").split():
            st.append([0, str(float(spectype)), '',': ', 'NIR', 'added by SpectreCell'])
            print(spectype)
elif 'sd' in new_objects['SPTNIRNAME'][i]:
    for spectype in new_objects['SPTNIRNAME'][i].strip("sd").split():
            st.append([0, str(float(spectype)), '', 'sd ', 'NIR', 'added by SpectreCell'])
            print(spectype)
elif 'blue' in new_objects['SPTNIRNAME'][i]:
    for spectype in new_objects['SPTNIRNAME'][i].strip("(blue)").split():
            st.append([0, str(float(spectype)), '', 'blue ', 'NIR', 'added by SpectreCell'])
            print(spectype)
else:
    print(new_objects['SPTNIRNAME'][i])

st.append([0, float(spectype), grav, suffix, 'NIR', 'added by SpectreCell'])

        new_objects['SPTNIRNAME'][i].replace('p','')


if ':' in new_objects['SPTNIRNAME'][i]:
    for spectype in new_objects['SPTNIRNAME'][i].strip(":").split():
        try:
            st.append([0, str(float(spectype)), '',':', 'NIR', 'added by SpectreCell'])
        except ValueError:
            print(spectype)
            pass
elif 'sd' in new_objects['SPTNIRNAME'][i]:
    for spectype in new_objects['SPTNIRNAME'][i].strip("sd").split():
        try:
            st.append([0, str(float(spectype)), '', 'sd', 'NIR', 'added by SpectreCell'])
        except ValueError:
            print(spectype)
            pass
elif 'blue' in new_objects['SPTNIRNAME'][i]:
    for spectype in new_objects['SPTNIRNAME'][i].strip("sd").split():
        try:
            st.append([0, str(float(spectype)), '', 'sd', 'NIR', 'added by SpectreCell'])
        except ValueError:
            print(spectype)
            pass

else:

st


st.append([0, str(float(spectype.strip(':'))), '',':', 'NIR', 'added by SpectreCell'])


new_objects['SPTNIRNAME'].dropna().values


new_objects['SPTOPTNAME'][643]










for i in range(len(matches)):
    if len(db.search((matches['RA'].iloc[[i]], matches['DEC'].iloc[[i]]), 'parallaxes', radius=0.00278, fetch=True)) > 1:
        print(int(matches.iloc[[i]]['source_id'].values[0]))
    else:
        print(i,' has just one parallax')












print(int(matches.iloc[[i]]['source_id'].values[0]))









db.search(new_objects['DISCOVERYREFNAME'].iloc[3], 'publications')










within20=pd.DataFrame(columns=list(new_objects.columns.values))
within40=pd.DataFrame(columns=list(new_objects.columns.values))
within60=pd.DataFrame(columns=list(new_objects.columns.values))
within100=pd.DataFrame(columns=list(new_objects.columns.values))
new_objects=leftover
leftover=pd.DataFrame(columns=list(new_objects.columns.values))

for i in range(len(within20)):
    results=db.search((within20['RA'].iloc[i], within20['DEC'].iloc[i]), 'sources', radius=0.00555556, fetch=True)
    if len(results)>1:
        print(results)

for i in range(len(within20)):
    results=db.search(within20['SHORTNAME'].iloc[i], 'sources', radius=0.00555556, fetch=True)
    if len(results)>1:
        print(results)


SkyCoord(ra=new_objects['RA'][0], dec=new_objects['DEC'][0], unit=(u.degree, u.degree))

db.table()

db.help()
