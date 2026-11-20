def area(  **params):
        """
        This provides a means to show or hide a bbox selection map.

        This method is dependent on the parameter 'spatialselectionstype' being
        set to 'bbox'.
        """
        name = params.get("parameter_name")
        spatial_selections_type = params.get("spatialselectionstype")
        if spatial_selections_type == "bbox":
            return  (name, [""])
        return (name,None)

def ensemblemembers(  **params):
    """
    Provide a list of ensembles.

    This method is dependent on the parameters 'collection' and 'variable' and
    optionally scenario being set.
    """
    name = params.get("parameter_name")
    collection = params.get("collection")
    scenario = params.get("scenario")

    if collection == "land-gcm" and scenario is not None and scenario == "rcp26":
        values = [
            "01",
            "02",
            "03",
            "04",
            "05",
            "06",
            "07",
            "08",
            "09",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "17",
            "21",
            "24",
            "25",
            "26",
            "27",
            "28",
        ]
        labels = [
            "HadGEM3-GC3.05-r001i1p00000",
            "HadGEM3-GC3.05-r001i1p00605",
            "HadGEM3-GC3.05-r001i1p00834",
            "HadGEM3-GC3.05-r001i1p01113",
            "HadGEM3-GC3.05-r001i1p01554",
            "HadGEM3-GC3.05-r001i1p01649",
            "HadGEM3-GC3.05-r001i1p01843",
            "HadGEM3-GC3.05-r001i1p01935",
            "HadGEM3-GC3.05-r001i1p02123",
            "HadGEM3-GC3.05-r001i1p02242",
            "HadGEM3-GC3.05-r001i1p02305",
            "HadGEM3-GC3.05-r001i1p02335",
            "HadGEM3-GC3.05-r001i1p02491",
            "HadGEM3-GC3.05-r001i1p02832",
            "HadGEM3-GC3.05-r001i1p02868",
            "bcc-csm1-1-r1i1p1",
            "CCSM4-r1i1p1",
            "CNRM-CM5-r1i1p1",
            "HadGEM2-ES-r1i1p1",
            "IPSL-CM5A-MR-r1i1p1",
            "MPI-ESM-MR-r1i1p1",
            "MRI-CGCM3-r1i1p1",
            "GFDL-ESM2G-r1i1p1",
        ]

    else:
        values = [
            "01",
            "02",
            "03",
            "04",
            "05",
            "06",
            "07",
            "08",
            "09",
            "10",
            "11",
            "12",
            "13",
            "14",
            "15",
            "16",
            "17",
            "18",
            "19",
            "20",
            "21",
            "22",
            "23",
            "24",
            "25",
            "26",
            "27",
            "28",
        ]
        labels = [
            "HadGEM3-GC3.05-r001i1p00000",
            "HadGEM3-GC3.05-r001i1p00605",
            "HadGEM3-GC3.05-r001i1p00834",
            "HadGEM3-GC3.05-r001i1p01113",
            "HadGEM3-GC3.05-r001i1p01554",
            "HadGEM3-GC3.05-r001i1p01649",
            "HadGEM3-GC3.05-r001i1p01843",
            "HadGEM3-GC3.05-r001i1p01935",
            "HadGEM3-GC3.05-r001i1p02123",
            "HadGEM3-GC3.05-r001i1p02242",
            "HadGEM3-GC3.05-r001i1p02305",
            "HadGEM3-GC3.05-r001i1p02335",
            "HadGEM3-GC3.05-r001i1p02491",
            "HadGEM3-GC3.05-r001i1p02832",
            "HadGEM3-GC3.05-r001i1p02868",
            "bcc-csm1-1-r1i1p1",
            "CCSM4-r1i1p1",
            "CESM1-BGC-r1i1p1",
            "CanESM2-r1i1p1",
            "CMCC-CM-r1i1p1",
            "CNRM-CM5-r1i1p1",
            "EC-EARTH-r1i1p1",
            "ACCESS1-3-r1i1p1",
            "HadGEM2-ES-r1i1p1",
            "IPSL-CM5A-MR-r1i1p1",
            "MPI-ESM-MR-r1i1p1",
            "MRI-CGCM3-r1i1p1",
            "GFDL-ESM2G-r1i1p1",
        ]

    return  (
        name, values, labels, "information"
    )

def ensemblememberset(  **params):
    """
    Provide a list of ensemble sets.

    This method is dependent on the parameter 'variable' being
    set.
    """
    name = params.get("parameter_name")
    variable = params.get("variable")
    collection = params.get("collection")
    scenario = params.get("scenario")

    if (
        collection is not None
        and collection == "land-gcm"
        and scenario is not None
        and scenario == "rcp26"
    ):
        values = ["land-rcm", "hadley-15", "land-gcm"]
        labels = [
            "Subset: regional 12km set only (12 members)",
            "Subset: PPE-15, Hadley Centre Model only (15 members)",
            "Subset: PPE-15, Hadley Centre Model (15 members) and selected CMIP 5 members",
        ]

    elif (
        collection is not None
        and collection == "land-derived"
        and variable
        in [
            "hursAnom",
            "sfcWindAnom",
            "uasAnom",
            "vasAnom",
            "hurs",
            "sfcWind",
            "uas",
            "vas",
        ]
    ):
        values = ["land-rcm", "hadley-15", "land-gcm"]
        labels = [
            "Subset: regional 12km set only (12 members)",
            "Subset: PPE-15, Hadley Centre Model only (15 members)",
            "Subset: PPE-15, Hadley Centre Model (15 members) and selected CMIP 5 members",
        ]

    elif variable in ["prAnom", "tasAnom", "pr", "tas"]:
        values = ["land-gcm", "land-rcm", "hadley-15"]
        labels = [
            "Full global set (28 members)",
            "Subset: regional 12km set only (12 members)",
            "Subset: PPE-15, Hadley Centre Model only (15 members)",
        ]
    else:
        values = ["land-rcm", "hadley-15"]
        labels = [
            "Subset: regional 12km set only (12 members)",
            "Subset: PPE-15, Hadley Centre Model only (15 members)",
        ]

    return  (
        name, values,labels,"information"
    )

def fontsize(  **params):
    """
    Provide a list of fonts.

    This method is dependent on the parameter 'imagesize' being
    set to '900', '1200' or '2400'.
    """
    name = params.get("parameter_name")
    image_size = params.get("imagesize")
    if image_size == "900":
        values = ["s", "m", "l"]
        labels = ["Small (recommended)", "Medium", "Large"]
    elif image_size == "1200":
        values = ["s", "m", "l"]
        labels = ["Small", "Medium (recommended)", "Large"]
    elif image_size == "2400":
        values = ["s", "m", "l"]
        labels = ["Small", "Medium", "Large (recommended)"]

    package_response =  (
        name, values, labels,"information"
    )
    return package_response

def showboundaries(  **params):
    """
    Provide a list of boundary types to show on maps.

    This method is dependent on the parameter 'spatialselectionstype' being
    set to 'bbox'.
    """
    name = params.get("parameter_name")
    spatial_selections_type = params.get("spatialselectionstype")
    if spatial_selections_type == "bbox":
        values = ["admin_region", "river_basin", "country"]
        labels = [
            "Overlay Admin Regions",
            "Overlay River Basins",
            "Overlay UK Countries",
        ]
        return  (name, values,   labels)
    return  (name,     None)

def baseline(**params):
        name = params.get("parameter_name")
        climate_change_type = params.get("climatechangetype")
        if climate_change_type != "anomaly":
            return (name, None)

        values = [ "b8100", "b8110"]
        labels = ["1981-2000", "1981-2010"]

        return (name, values, labels, "information")


def showprobabilitylevels(  **params):
    """
    This provides a way to show or hide a tick box.

    This method is dependent on the parameters 'baseline', 'scenario' and
    'variable'.
    """
    name = params.get("parameter_name")
    baseline = params.get("baseline")
    scenario = params.get("scenario")
    variable = params.get("variable")

    if (
        baseline == "b8100"
        and scenario in ["rcp26", "rcp45", "rcp60", "rcp85", "sres-a1b"]
        and variable
        in [
            "cltAnom",
            "hussAnom",
            "prAnom",
            "pslAnom",
            "rlsAnom",
            "rsdsAnom",
            "rssAnom",
            "tasAnom",
            "tasmaxAnom",
            "tasminAnom",
        ]
    ):
        return  (name, [""])
    return  (name,     None)


def timeslice_12km(**params):
    """
        This provides the range for a date picker.

        This method is dependent on the parameters 'scenario' and 'ensemble'.
        """
    TIMESLICES = {
    "01": ["2017", "2037", "2037", "2057", "2051", "2071"],
    "04": ["2014", "2034", "2034", "2054", "2048", "2068"],
    "05": ["2019", "2039", "2040", "2060", "2054", "2074"],
    "06": ["2016", "2036", "2036", "2056", "2052", "2072"],
    "07": ["2018", "2038", "2038", "2058", "2052", "2072"],
    "08": ["2020", "2040", "2040", "2060", "2057", "2077"],
    "09": ["2016", "2036", "2032", "2052", "2045", "2065"],
    "10": ["2018", "2038", "2037", "2057", "2055", "2075"],
    "11": ["2015", "2035", "2036", "2056", "2051", "2071"],
    "12": ["2023", "2043", "2041", "2061", "2054", "2074"],
    "13": ["2016", "2036", "2037", "2057", "2051", "2071"],
    "15": ["2019", "2039", "2040", "2060", "2055", "2075"],
    }
    name = params.get("parameter_name")
    scenario = params.get("scenario")
    ensemble = params.get("ensemblememberset")
    timeslice = TIMESLICES[ensemble]
    if scenario == "gwl2":
        values = [timeslice[0], timeslice[1]]
    elif scenario == "gwl3":
        values = [timeslice[2], timeslice[3]]
    elif scenario == "gwl4":
        values = [timeslice[4], timeslice[5]]
    
    return  (
        name, values,   values,    "information"
    )




def timeslice(  **params):
    """
    Provide a minimum and maximum year for a range slider.

    This method is dependent on the parameter 'collection' being set to 'land-prob',
    'land-gcm' or 'land-rcm'. An adjustment is made if the temporalaverage is "dec".

    """
    name = params.get("parameter_name")
    collection = params.get("collection")
    temporal_average = params.get("temporalaverage")
    if collection == "land-prob":
        if temporal_average == "dec":
            values = ["1961", "2099"]
        else:
            values = ["1961", "2100"]

    elif collection == "land-gcm":
        if temporal_average == "dec":
            values = ["1900", "2099"]
        else:
            values = ["1900", "2100"]

    elif collection == "land-rcm":
        if temporal_average == "dec":
            values = ["1980", "2080"]
        else:
            values = ["1981", "2081"]

    return  (
        name, values,   values,    "information"
    )

def timeslice2(  **params):
    """
    This provides a means to show or hide a selection box.

    This method is dependent on the parameter 'timesliceduration' being
    set to '30y' or '20y'.
    """
    name = params.get("parameter_name")
    time_slice_duration = params.get("timesliceduration")
    if time_slice_duration == "30y":
        values = [
            "2010-2039",
            "2020-2049",
            "2030-2059",
            "2040-2069",
            "2050-2079",
            "2060-2089",
            "2070-2099",
        ]
        labels = [
            "2010-2039 (2020s)",
            "2020-2049 (2030s)",
            "2030-2059 (2040s)",
            "2040-2069 (2050s)",
            "2050-2079 (2060s)",
            "2060-2089 (2070s)",
            "2070-2099 (2080s)",
        ]

        return  (name, values, labels)
    elif time_slice_duration == "20y":
        values = [
            "2010-2029",
            "2020-2039",
            "2030-2049",
            "2040-2059",
            "2050-2069",
            "2060-2079",
            "2070-2089",
            "2080-2099",
        ]
        labels = [
            "2010-2029",
            "2020-2039",
            "2030-2049",
            "2040-2059",
            "2050-2069",
            "2060-2079",
            "2070-2089",
            "2080-2099",
        ]

        return  (name, values, labels)
    return  (name,     None)

def timeslicercm(  **params):
    """
    This provides a means to show or hide a selection box.

    This method is dependent on the parameter 'timesliceduration' being
    set to '30y' or '20y'.
    """
    name = params.get("parameter_name")
    time_slice_duration = params.get("timesliceduration")
    if time_slice_duration == "30y":
        values = ["2010-2039", "2020-2049", "2030-2059", "2040-2069", "2050-2079"]
        labels = [
            "2010-2039 (2020s)",
            "2020-2049 (2030s)",
            "2030-2059 (2040s)",
            "2040-2069 (2050s)",
            "2050-2079 (2060s)",
        ]

        return  (name, values, labels)
    elif time_slice_duration == "20y":
        values = [
            "2010-2029",
            "2020-2039",
            "2030-2049",
            "2040-2059",
            "2050-2069",
            "2060-2079",
        ]
        labels = [
            "2010-2029",
            "2020-2039",
            "2030-2049",
            "2040-2059",
            "2050-2069",
            "2060-2079",
        ]

        return  (name, values, labels)
    return  (name,     None)

def timeslicecpm(  **params):
    """
    This provides a means to show or hide a selection box.

    This method is dependent on the parameter 'timesliceduration' being
    set to '20y'.
    """
    name = params.get("parameter_name")
    time_slice_duration = params.get("timesliceduration")
    if time_slice_duration == "20y":
        values = ["2021-2040", "2061-2080"]
        labels = ["2021-2040", "2061-2080"]

        return  (name, values, labels)
    return  (name,     None)

def timesliceduration(  **params):
    """
    Provides a list of time slice durations.

    This method is dependent on the parameter 'baseline' being
    set to 'b8100' for 20 years, otherwise 30 years is assumed.
    """
    name = params.get("parameter_name")
    baseline = params.get("baseline")
    scenario = params.get("scenario")
    if scenario is not None and scenario in ["gwl2", "gwl4"]:
        values = ["", "1y"]
        labels = ["", "1 year"]
    elif baseline == "b8100":
        values = ["1y", "20y"]
        labels = ["1 year", "20 years"]
    elif baseline in ["b6190", "b8110"]:
        values = ["1y", "30y"]
        labels = ["1 year", "30 years"]
    return  (name, values, labels)

def timeslicedurationprob(  **params):
    """
    Provides a list of time slice durations.

    This method is dependent on the parameter 'baseline' being
    set to 'b8100' for 20 years, otherwise 30 years is assumed.
    """
    name = params.get("parameter_name")
    baseline = params.get("baseline")
    if baseline == "b8100":
        values = ["1y", "20y"]
        labels = ["1 year", "20 years"]
    elif baseline in ["b6190", "b8110"]:
        values = ["", "30y"]
        labels = ["", "30 years"]
    return  (name, values, labels)

def variable(  **params):
    """
    Provide a list of variables.

    This method is dependent on the parameter 'climatechangetype' being
    set to 'absolute' or 'anomaly' and on the parameter 'collection'
    """
    name = params.get("parameter_name")
    climate_change_type = params.get("climatechangetype")
    collection = params.get("collection")
    values = []
    labels = []
    if collection == "land-cpm":
        values, labels = _variable_cpm(climate_change_type)

    if collection == "land-gcm":
        values, labels = _variable_cpm(climate_change_type)

    elif collection == "land-rcm":
        values, labels = _variable_rcm(climate_change_type)

    return  (
        name, values,   labels,    "information"
    )

def _variable_cpm(  climate_change_type):
    values = []
    labels = []
    if climate_change_type == "absolute":
        values = [
            "tas",
            "pr",
            "tasmax",
            "tasmin",
            "sfcWind",
            "wsgmax10m",
            "hurs",
            "huss",
            "uas",
            "vas",
            "prsn",
            "snw",
            "psl",
            "rls",
            "rss",
            "clt",
        ]
        labels = [
            "Mean air temperature at 1.5m (�C)",
            "Precipitation rate (mm/day)",
            "Maximum air temperature at 1.5m (�C)",
            "Minimum air temperature at 1.5m (�C)",
            "Wind speed at 10m (m s-1)",
            "Wind speed gust maximum (m s-1)",
            "Relative humidity at 1.5m (%)",
            "Specific humidity at 1.5m (1)",
            "Eastward wind at 10m (m s-1)",
            "Northward wind at 10m (m s-1)",
            "Snowfall flux (mm/day)",
            "Surface snow amount (mm)",
            "Sea level pressure (hPa)",
            "Net Surface long wave flux (W m-2)",
            "Net Surface short wave flux (W m-2)",
            "Total cloud (%)",
        ]

    elif climate_change_type == "anomaly":
        values = [
            "tasAnom",
            "prAnom",
            "tasmaxAnom",
            "tasminAnom",
            "sfcWindAnom",
            "wsgmax10mAnom",
            "hursAnom",
            "hussAnom",
            "uasAnom",
            "vasAnom",
            "prsnAnom",
            "snwAnom",
            "pslAnom",
            "rlsAnom",
            "rssAnom",
            "cltAnom",
        ]
        labels = [
            "Mean air temperature anomaly at 1.5m (�C)",
            "Precipitation rate anomaly (%)",
            "Maximum air temperature anomaly at 1.5m (�C)",
            "Minimum air temperature anomaly at 1.5m (�C)",
            "Wind speed anomaly at 10m (m s-1)",
            "Wind speed gust maximum anomaly (m s-1)",
            "Relative humidity percentage change anomaly at 1.5m (%)",
            "Specific humidity percentage change anomaly at 1.5m (%)",
            "Eastward wind anomaly at 10m (m s-1)",
            "Northward wind anomaly at 10m (m s-1)",
            "Snowfall flux anomaly (%)",
            "Surface snow amount anomaly (mm)",
            "Sea level pressure anomaly (hPa)",
            "Net Surface long wave flux anomaly (W m-2)",
            "Net Surface short wave flux anomaly (W m-2)",
            "Total cloud anomaly (%)",
        ]

    return values, labels

def _variable_rcm(  climate_change_type):
    values = []
    labels = []

    if climate_change_type == "absolute":
        values = [
            "tas",
            "pr",
            "tasmax",
            "tasmin",
            "sfcWind",
            "hurs",
            "huss",
            "uas",
            "vas",
            "prsn",
            "snw",
            "psl",
            "rls",
            "rss",
            "clt",
        ]
        labels = [
            "Mean air temperature at 1.5m (�C)",
            "Precipitation rate (mm/day)",
            "Maximum air temperature at 1.5m (�C)",
            "Minimum air temperature at 1.5m (�C)",
            "Wind speed at 10m (m s-1)",
            "Relative humidity at 1.5m (%)",
            "Specific humidity at 1.5m (1)",
            "Eastward wind at 10m (m s-1)",
            "Northward wind at 10m (m s-1)",
            "Snowfall flux (mm/day)",
            "Surface snow amount (mm)",
            "Sea level pressure (hPa)",
            "Net Surface long wave flux (W m-2)",
            "Net Surface short wave flux (W m-2)",
            "Total cloud (%)",
        ]

    elif climate_change_type == "anomaly":
        values = [
            "tasAnom",
            "prAnom",
            "tasmaxAnom",
            "tasminAnom",
            "sfcWindAnom",
            "hursAnom",
            "hussAnom",
            "uasAnom",
            "vasAnom",
            "prsnAnom",
            "snwAnom",
            "pslAnom",
            "rlsAnom",
            "rssAnom",
            "cltAnom",
        ]
        
        labels = [
            "Mean air temperature anomaly at 1.5m (�C)",
            "Precipitation rate anomaly (%)",
            "Maximum air temperature anomaly at 1.5m (�C)",
            "Minimum air temperature anomaly at 1.5m (�C)",
            "Wind speed anomaly at 10m (m s-1)",
            "Relative humidity percentage change anomaly at 1.5m (%)",
            "Specific humidity percentage change anomaly at 1.5m (%)",
            "Eastward wind anomaly at 10m (m s-1)",
            "Northward wind anomaly at 10m (m s-1)",
            "Snowfall flux anomaly (%)",
            "Surface snow amount anomaly (mm)",
            "Sea level pressure anomaly (hPa)",
            "Net Surface long wave flux anomaly (W m-2)",
            "Net Surface short wave flux anomaly (W m-2)",
            "Total cloud anomaly (%)",
        ]

    return values, labels

def yeargcm(  **params):
    """
    This provides a means to show or hide a data picker.

    This method is dependent on the parameter 'timesliceduration' being
    set to '1y'. An adjustment is made if the temporalaverage is "dec".

    """
    name = params.get("parameter_name")
    time_slice_duration = params.get("timesliceduration")
    temporal_average = params.get("temporalaverage")

    if time_slice_duration != "1y":
        return  (name,     None)

    if temporal_average == "dec":
        return  (name,     ["1900", "2098"])

    return  (name,     ["1900", "2099"])

def yearprob(  **params):
    """
    This provides a means to show or hide a data picker.

    This method is dependent on the parameter 'timesliceduration' being
    set to '1y'. An adjustment is made if the temporalaverage is "dec".

    """
    name = params.get("parameter_name")
    time_slice_duration = params.get("timesliceduration")
    temporal_average = params.get("temporalaverage")

    if time_slice_duration != "1y":
        return  (name,     None)

    if temporal_average == "dec":
        return  (name,     ["1961", "2098"])

    return  (name,     ["1961", "2099"])

def yearrcm(  **params):
    """
    This provides a means to show or hide a data picker.

    This method is dependent on the parameter 'timesliceduration' being
    set to '1y'. An adjustment is made if the temporalaverage is "dec".

    """
    name = params.get("parameter_name")
    time_slice_duration = params.get("timesliceduration")
    temporal_average = params.get("temporalaverage")

    if time_slice_duration != "1y":
        return  (name,     None)

    if temporal_average == "dec":
        return  (name,     ["1980", "2079"])

    return  (name,     ["1981", "2080"])

def yearcpm(  **params):
    """
    This provides a means to show or hide a list of years for CPM.

    This method is dependent on the parameter 'timesliceduration' being
    set to '1y'.
    """
    name = params.get("parameter_name")
    time_slice_duration = params.get("timesliceduration")
    temporal_average = params.get("temporalaverage")
    if time_slice_duration == "1y":
        values = [
            "1981",
            "1982",
            "1983",
            "1984",
            "1985",
            "1986",
            "1987",
            "1988",
            "1989",
            "1990",
            "1991",
            "1992",
            "1993",
            "1994",
            "1995",
            "1996",
            "1997",
            "1998",
            "1999",
            "2000",
            "2021",
            "2022",
            "2023",
            "2024",
            "2025",
            "2026",
            "2027",
            "2028",
            "2029",
            "2030",
            "2031",
            "2032",
            "2033",
            "2034",
            "2035",
            "2036",
            "2037",
            "2038",
            "2039",
            "2040",
            "2061",
            "2062",
            "2063",
            "2064",
            "2065",
            "2066",
            "2067",
            "2068",
            "2069",
            "2070",
            "2071",
            "2072",
            "2073",
            "2074",
            "2075",
            "2076",
            "2077",
            "2078",
            "2079",
        ]
        labels = [
            "1981",
            "1982",
            "1983",
            "1984",
            "1985",
            "1986",
            "1987",
            "1988",
            "1989",
            "1990",
            "1991",
            "1992",
            "1993",
            "1994",
            "1995",
            "1996",
            "1997",
            "1998",
            "1999",
            "2000",
            "2021",
            "2022",
            "2023",
            "2024",
            "2025",
            "2026",
            "2027",
            "2028",
            "2029",
            "2030",
            "2031",
            "2032",
            "2033",
            "2034",
            "2035",
            "2036",
            "2037",
            "2038",
            "2039",
            "2040",
            "2061",
            "2062",
            "2063",
            "2064",
            "2065",
            "2066",
            "2067",
            "2068",
            "2069",
            "2070",
            "2071",
            "2072",
            "2073",
            "2074",
            "2075",
            "2076",
            "2077",
            "2078",
            "2079",
        ]
        # there is no December data for 2080
        if temporal_average != "dec":
            values.append("2080")
            labels.append("2080")

        return  (name, values, labels)

    return  (name,     None)

