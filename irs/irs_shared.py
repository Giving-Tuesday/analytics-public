"""
Download parts of the IRS Form 990 extract.
"""
# https://givingtuesday.cloud.looker.com/sql/4s2j5yznd8qb6c
from classypy.io.irs import IrsTaxExtractDataset, IrsEOBMFDataset
from classypy.util.caching import cache_dataframe

ntee_category_groups = {
    "A": "I",
    "B": "II",
    "C": "III",
    "D": "III",
    "E": "IV",
    "F": "IV",
    "G": "IV",
    "H": "IV",
    "I": "V",
    "J": "V",
    "K": "V",
    "L": "V",
    "M": "V",
    "N": "V",
    "O": "V",
    "P": "V",
    "Q": "VI",
    "R": "VII",
    "S": "VII",
    "T": "VII",
    "U": "VII",
    "V": "VII",
    "W": "VII",
    "X": "VIII",
    "Y": "IX",
    "Z": "X"
}

ntee_major_group_names = {
    "I": "Arts, Culture, and Humanities",
    "II": "Education",
    "III": "Environment and Animals",
    "IV": "Health",
    "V": "Human Services",
    "VI": "International, Foreign Affairs",
    "VII": "Public, Societal Benefit",
    "VIII": "Religion Related",
    "IX": "Mutual/Membership Benefit",
    "X": "Unknown, Unclassified",
}


# Get the data
@cache_dataframe(default_csv_file="tax_extract_4years.csv")
def get_yearly_data():
    dataset = IrsTaxExtractDataset()
    return dataset.fetch(years=(2016, 2017, 2018, 2019), verbose=2)


@cache_dataframe(default_csv_file="eobmf.csv")
def get_entity_data():
    dataset = IrsEOBMFDataset()
    return dataset.fetch()


@cache_dataframe(default_csv_file="annotated_irs_2018.csv")
def get_annotated_2018():
    df = get_yearly_data(csv_file="tax_extract_4years.csv")
    dfe = get_entity_data(csv_file="eobmf.csv")

    # Augment
    df['contributions'] = df['totcntrbgfts'].fillna(0) + df['totcntrbs'].fillna(0)
    df['tax_year'] = df['tax period'].map(lambda y: int(y[:4]) if isinstance(y, str) else y.year)
    # Filter
    df = df[df['tax_year'].isin([2015, 2016, 2017, 2018])]
    df = df[['contributions', 'EIN', 'tax_year']]
    # Dedupe
    df = df.groupby(["EIN", "tax_year"]).last().reset_index()

    # Buckets
    df.loc[:, 'bucket'] = df['contributions'].map(lambda c: '0. None' if c<=0 else ('1. <100k' if c<100e3 else ('2. 100k-250k' if c<250e3 else ('3. 250k-1M' if c<1e6 else ('4. 1M-5M' if c<5e6 else ('5. 5M-25' if c<25e6 else '6. 25M+'))))))  # noqa

    # Transformations
    eins = df.groupby('EIN')['contributions'].count().to_frame()
    df2 = df[df['EIN'].isin(eins[eins['contributions'] == 3].index.values)]
    df2 = df2.sort_values(["EIN", "tax_year"])

    # Works because of positive sort above
    df2["growth"] = (df2['contributions'] / df2['contributions'].shift(1)) - 1
    df2['last_bucket'] = df2['bucket'].shift(1)
    df2['last_contributions'] = df2['bucket'].shift(1)

    #
    df3 = df2[df2['tax_year'].isin([2017, 2018])]
    eins = df3.groupby('EIN')['contributions'].count().to_frame()
    df3 = df2[df2['EIN'].isin(eins[eins['contributions'] == 2].index.values)]
    df3 = df3[df3.tax_year == 2018]

    #
    df5 = df3.merge(dfe[["ein", "ntee_cd"]], left_on="EIN", right_on="ein", how="left")
    df5["nteegrp"] = (
        df5.ntee_cd
        .fillna("")
        .map(lambda c: ntee_major_group_names[ntee_category_groups.get((c or "Z")[0], "X")])
    )

    return df5


@cache_dataframe(default_csv_file="annotated_irs_2018_filtered.csv")
def get_filtered_2018():
    df3 = get_annotated_2018()
    df4 = df3[df3['contributions'] >= 5000]
    df4 = df4[df4['growth'].between(-0.667, 3)]

    return df4
