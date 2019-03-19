# Continue building and improving your code today!

## New Object loops

 - Continue working on your For-loops to add the new_objects data to the Database.

  1. new_objects column names needed for parallax table
    1. 'PARALLAX'
    2. 'PARALLAX_ERROR'

  2. new_objects column names needed for proper_motions table
    1. 'PMRA'
    2. 'PMRA_ERROR'
    3. 'PMDEC'
    4. 'PMDEC_ERROR'
  3. new_objects column names needed for photometry table
    1. 'PHOT_G_MEAN_MAG'
    2. 'PHOT_G_MEAN_MAG_ERROR'
    3. 'PHOT_BP_MEAN_MAG'
    4. 'PHOT_BP_MEAN_MAG_ERROR'
    5. 'PHOT_RP_MEAN_MAG'
    6. 'PHOT_RP_MEAN_MAG_ERROR'
    7. 'TMASSJ'
    8. 'TMASSJERR'
    9. 'TMASSH'
    10. 'TMASSHERR'
    11. 'TMASSK'
    12. 'TMASSKERR'
    13. 'WISEW1'
    14. 'WISEW1ERR'
    15. 'WISEW2'
    16. 'WISEW2ERR'
    17. 'WISEW3'
    18. 'WISEW3ERR'
    19. 'GUNNG'
    20. 'GUNNGERR'
    21. 'GUNNR'
    22. 'GUNNRERR'
    23. 'GUNNI'
    24. 'GUNNIERR'
    25. 'GUNNZ'
    26. 'GUNNZERR'
    27. 'GUNNY'
    28. 'GUNNYERR'


Work with your same partner from Thursday (slack the group when you're finished!)


The `len()` of each of your tables should be:
  1. `len(parallax_data)` = 456

  2. `len(propermotions_data)` = 456

  3. `len(photometry_data)` = 6371


Add your tables to the database!

**remember!:**
- don't add to the database until your table looks correct
- get the source ID by searching the database
  - `db.search()` will return a **row** of data. Use the column names and indexes to select **only the source id**.

**hints:**

`parallax_data = list()`

`propermotions_data = list()`

`photometry_data = list()`

`parallax_data.append(['source_id','parallax', 'parallax_unc','publication_shortname', 'adopted','comments'])`

`propermotions_data.append(['source_id','proper_motion_ra', 'proper_motion_ra_unc','proper_motion_dec', 'proper_motion_dec_unc','publication_shortname', 'comments'])`

`photometry_data.append(['source_id','band', 'magnitude','magnitude_unc', 'publication_shortname', 'comments'])`


<hr>

## Remove FAKE photometry from the database!

When photometry wasn't available for objects, -99999 is used instead of leaving the cell blank. We need to `db.modify()` to delete these entries!

Complete this query to confirm that you have **963** entries with a magnitude of -99999.0. (if you have a 'NoneType has no len()' error, make sure you've added your photometry_data table to the database)

  `len(db.query("SELECT * FROM photometry WHERE [COMPLETE THIS PART] AND comments='[COMPLETE THIS PART]'"))`

If the length is 963, go ahead and use your completed query to delete those entries

  `db.modify("DELETE FROM photometry WHERE [COMPLETE THIS PART] AND comments='[COMPLETE THIS PART]'")`

<hr>


# Make your code ITERATIVE!

Turn your code into functions!

You should have one function to generate (but NOT ADD) the tables for matches and another function to generate the tables for the new_objects tables.

Here's some code to get your functions started:

`def generateMatchtables(matches):`

`    [put your code here]`

`    return matchParallax_data, matchPropermotions_data, matchPhotometry_data`




`def generateNewObjtables(new_objects, db):`

`    [put your code here]`

`    return newObjParallax_data, newObjPropermotions_data, newObjPhotometry_data`
