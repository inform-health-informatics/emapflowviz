# Steve Harris
# 2019-11-03
# Theme hospital patient flow generator
# All times are in hours

rm(list=ls())
library(simmer)
library(simmer.plot)
library(data.table)
library(ggplot2)
library(janitor)

set.seed(3001)

# Set-up constants
LOS_MEAN_ED <-  4
LOS_MEAN_ICU <- 48 
LOS_MEAN_AMU <- 24
LOS_MEAN_T8 <- 96

N_PATIENTS <- 1e3


how_ill_in_ED <- function() {
  # Use this function to define paths by probability
  # return severity on interger scale for branching logic
  # 1 = not sick; hence discharge
  # 2 = sick; hence admit
  # 3 = very sick; hence ICU
  # sample.int(c(1:3), 1)
  # assign probabilites to the 3 paths above
  sample.int(3, 1, prob=c(0.5,0.4,0.1))
}

# qplot(replicate(1e2, how_ill_in_ED()))
# summary(rexp(1e3,1))

# bank server version but with infinite resources
patient <-
  trajectory("Patients's path") %>%
  # ED
  # =====
log_("ED arrive") %>%
  seize("ED") %>%
  timeout(function() rexp(1,1/2)) %>%
  release("ED") %>%
  
  # ========================
# ED branching logic STARTS
# ========================

branch(
  how_ill_in_ED, continue=c(FALSE, TRUE, TRUE),
  # ---
  trajectory() %>% 
    log_("Discharge from ED"),
  # ---
  trajectory() %>% 
    # AMU
    # =====
  log_("AMU arrive") %>%
    seize("AMU") %>%
    timeout(function() LOS_MEAN_AMU*rexp(1,1)) %>%
    release("AMU"),
  # ---
  trajectory() %>% 
    # ICU
    # =====
  log_("ICU arrive") %>%
    seize("ICU") %>%
    timeout(function() LOS_MEAN_ICU*rexp(1,1)) %>%
    release("ICU")
) %>%
  
  # ========================
# ED branching logic STOPS
# ========================

# T8
# =====
log_("T8 arrive") %>%
  seize("T8") %>%
  timeout(function() LOS_MEAN_T8*rexp(1,1)) %>%
  release("T8") %>%
  # Discharge
  # ====
log_(function() {paste("Finished: ", now(hospital))})

get_palette <- scales::brewer_pal(type = "qual", palette = 1)
plot(patient, fill = get_palette)

# return a vector of patient arrival times
generator_vector <- c(0, rexp(N_PATIENTS-1, 1/10), -1)

hospital <-
  simmer("hospital") %>%
  add_resource("ED", capacity=+Inf) %>% 
  add_resource("AMU", capacity=+Inf) %>% 
  add_resource("ICU", capacity=+Inf) %>% 
  add_resource("T8", capacity=+Inf) %>% 
  # one customer add_generator("Patient", patient, at(rexp(1, 1/5))) many
  # customers the function() {c(0, rexp(4, 1/10), -1)}) creates a vector with 6
  # items starting at 0; the -1 in the generator stops it
  add_generator("Patient", patient, function() {generator_vector}, mon=2)


hospital %>%  reset() %>%  run() %>% print()
dt_pts <- setDT(hospital %>% get_mon_arrivals(per_resource=TRUE))
dt_pts[order(name)]
dt_pts %>% tabyl(resource)

dt_pts[, rownum := .I][1:5]

# Now convert patients to long form events
dt_events <- melt.data.table(
  dt_pts, 
  id.vars=c("name", "resource"), 
  measure.vars=c("start_time", "end_time") )
# Now sort so you can drop duplicate times (where one start_time is the same as the preceding end_time)
dt_events <- dt_events[order(value, variable)]
dt_events <- unique(dt_events, by=c("name", "value"))
setnames(dt_events, "variable", "event")
setnames(dt_events, "resource", "ward")
setnames(dt_events, "value", "time")
# dt_events[1:5]


library(readr)
readr::write_csv(dt_pts, 'data/ADT.csv')
readr::write_csv(dt_events, 'data/ADT_events.csv')
dt_pts <- data.table(readr::read_csv('data/ADT.csv'))
dt_events <- data.table(readr::read_csv('data/ADT_events.csv'))



# Note that DBplyr is automatically used by Dplyr when working with databases
library(dplyr, warn.conflicts = FALSE)
library(DBI)

conn <- DBI::dbConnect(RPostgreSQL::PostgreSQL(),
                      dbname = "mart_flow",
                      host = "localhost",
                      user = "steve",
                      password = ""
)

dbListTables(conn)
dbReadTable(conn, "pts")
dbWriteTable(conn, "pts", dt_pts, overwrite=TRUE)
dbWriteTable(conn, "events", dt_events, overwrite=TRUE)
dbReadTable(conn, "pts")
head(dt_pts)

dbDisconnect(conn)
