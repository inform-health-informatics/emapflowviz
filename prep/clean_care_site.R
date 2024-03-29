# 2019-11-24
# Steve Harris
# TODO the care site table will need updating; it was exported on the date above but will inevitably change with time

# CRAN libraries
library(data.table)
library(assertthat)
library(readr)
library(stringr)

# devtools and github libraries
# First run
# devtools::install_github("bergant/airtabler")
library(airtabler)
# TODO move this into the .Renviron file
# follow instructions here to get key
# https://github.com/bergant/airtabler
# and for more details about how to construct the URLs s
# see https://airtable.com/appWUjERknFDJRBp1/api/docs#curl/introduction
# AIRTABLE_API_KEY <- stored in .Renviron
assert_that(nchar(Sys.getenv("AIRTABLE_API_KEY"))>0)
AIRTABLE_EMAP_BASE <- "appWUjERknFDJRBp1"


# load the current care sites
dt <- setDT(readr::read_csv("data/omop_live_care_site.csv"))
head(dt)
# initial split on ^ delimiter
dt[, c("ward", "room", "bed") := tstrsplit(care_site_name, "^", fixed=TRUE )][]
dt[,.(care_site_name, ward, room, bed)]

# now inspect and prob drop where room and bed not specified (assume these are OPD)
dt[bed != "null",.(care_site_name, ward, room, bed)]
dt[room != "null",.(care_site_name, ward, room, bed)]
dt <- dt[room != "null" & bed != "null",.(care_site_id, care_site_name, ward, room, bed)]

# DEFINE and merge on wards
# down to 1787
# View(dt[,.N,by=ward][order(ward)])
write_csv(dt[,.N,by=ward][order(ward)], "data/ward_keys.csv")

# DEFINE and merge on beds
# View(dt[,.N,by=bed][order(bed)])
beds_clean <- dt[, bednumber := str_match(bed, "^.*\\-(\\w?\\d+\\w?)$")[2],by=care_site_name]
beds_clean[, bay := ifelse(str_detect(bed, "^BY.+"),TRUE,FALSE)]
beds_clean[bay==TRUE]
beds_clean[, sideroom := ifelse(str_detect(bed, "^SR.+"),TRUE,FALSE)]
beds_clean[sideroom==TRUE]
beds_clean

# DEFINE and extract meaning from 'room'
dt[,.N,by=room]

dt[,mortimer_market := ifelse(str_detect(room, "MMKT"), TRUE, FALSE) ]
dt[,waiting_room := ifelse(str_detect(room, "WAIT"), TRUE, FALSE) ]
dt[,RNTNE := ifelse(str_detect(room, "RNTNE"), TRUE, FALSE) ]
dt[,ENT_ED := ifelse(str_detect(room, "ENTED"), TRUE, FALSE) ]
dt[,macmillan_cc := ifelse(str_detect(room, "MCU"), TRUE, FALSE) ]
dt[,CHALF := ifelse(str_detect(room, "CHALF"), TRUE, FALSE) ]
dt[,macmillan_cc := ifelse(str_detect(room, "MCC"), TRUE, FALSE) ]
dt[,POOL := ifelse(str_detect(room, "POOL"), TRUE, FALSE) ]
dt[,tottenham_court_road := ifelse(str_detect(room, "TCR"), TRUE, FALSE) ]
dt[,RLHIM := ifelse(str_detect(room, "RLHIM"), TRUE, FALSE) ]
dt[,UCH := ifelse(str_detect(room, "UCH"), TRUE, FALSE) ]
dt[,RESUS := ifelse(str_detect(room, "RESUS"), TRUE, FALSE) ]
dt[,MAJ := ifelse(str_detect(room, "MAJ"), TRUE, FALSE) ]
dt[,EDH := ifelse(str_detect(room, "EDH"), TRUE, FALSE) ]
dt[,MINORS := ifelse(str_detect(room, "MINO"), TRUE, FALSE) ]
dt[,patient_lounge := ifelse(str_detect(room, "PATLNGE"), TRUE, FALSE) ]


# grouping label for rooms
# dt$slug_room <- NULL
dt[ward=="ED", room]
dt[ward=="ED", slug_room := "OTHER"] # set to empty
dt[ward=="ED", slug_room := ifelse(str_detect(room, "RESUS"), "RESUS", slug_room) ]
dt[ward=="ED", slug_room := ifelse(str_detect(room, "MAJ"), "MAJORS", slug_room) ]
dt[ward=="ED", slug_room := ifelse(str_detect(room, "UTC"), "UTC", slug_room) ]
dt[ward=="ED", slug_room := ifelse(str_detect(room, "PAEDS"), "PAEDS", slug_room) ]
dt[ward=="ED", slug_room := ifelse(str_detect(room, "TRIAGE"), "TRIAGE", slug_room) ] # NB overwrites PAEDS TRIAGE
dt[ward=="ED", slug_room := ifelse(str_detect(room, "RAT"), "RAT", slug_room) ]
dt[ward=="ED", slug_room := ifelse(str_detect(room, "OTF"), "OTHER", slug_room) ]
dt[ward=="ED", slug_room := ifelse(str_detect(room, "DIAGNOSTICS"), "DIAGNOSTICS", slug_room) ]
table(dt$slug_room)

# Now merge with original datatable
# for wards via Airtable hand updated key
EMAP_DATAFIELDS <-
  airtable(
    base = AIRTABLE_EMAP_BASE,
    tables = c("EMAP fields", "ward_lookup")
  )

ward_lookup <- data.table(EMAP_DATAFIELDS$ward_lookup$select())
mdt <- dt
mdt <- ward_lookup[,.(ward_hl7,building,slug)][mdt, on=c("ward_hl7==ward"), ]
setnames(mdt, "ward_hl7", "ward")
mdt

setcolorder(mdt, c(
  "care_site_id",
  "care_site_name",
  "ward",
  "room",
  "bed"
))

# Save to csv for local processing
write_csv(mdt, "app/static/data/care_site_clean.csv")
# Finally push this back to airtable

