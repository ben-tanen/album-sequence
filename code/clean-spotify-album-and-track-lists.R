rm(list = ls())

library(tidyverse)
library(tidylog)

setwd("~/Desktop/Projects/album-sequence/")

# helper function to manually choose matches when multiple options
manual_dedupe_match <- function(data, 
                                id_cols.main,
                                id_cols.matches) {

# report the number of groups with matches + number of matches
data %>%
  group_by_at(id_cols.main) %>%
  summarise(n_matches = n(),
            .groups = "drop") %>%
  count(n_matches, name = "n_groups") %>%
  mutate(pct = n_groups / sum(n_groups)) %>%
  print()

data.w_matches <- data %>%
  mutate(row = row_number()) %>%
  group_by_at(id_cols.main) %>%
  mutate(n_matches = n()) %>%
  ungroup() %>%
  mutate(correct = if_else(n_matches == 1, TRUE, FALSE))

groups <- data.w_matches %>%
  filter(n_matches > 1) %>%
  distinct_at(id_cols.main)

for (row in 1:nrow(groups)) {
  group <- groups[row,]
  group_rows <- data.w_matches %>%
    inner_join(group, by = id_cols.main)
  
  cat("for group:\n")
  print(as.data.frame(group))
  cat("\nwhich row is correct?\n")
  print(group_rows %>% 
          select(id_cols.matches) %>%
          as.data.frame())
  selection <- readline(prompt = "correct row: ")
  data.w_matches <- group_rows[selection,] %>%
    select(c(id_cols.main, id_cols.matches)) %>%
    mutate(correct2 = TRUE) %>%
    right_join(data.w_matches,
               by = c(id_cols.main, id_cols.matches)) %>%
    mutate(correct = if_else(!is.na(correct2), correct2, correct)) %>%
    select(names(data.w_matches)) %>%
    arrange(row)
}

data.w_matches %>%
  filter(correct) %>%
  select(-row, -n_matches, -correct) %>%
  return()

}

# import all album matches (including popularity)
dt.raw <- read.csv("data/02_spotify_album_list_w_popularity_20210602.csv", quote = "\"") %>%
  as_tibble()

# if album name + artist is the same, just take the most popular
# and remove any options that have popularity = 0 (if other options exist)
dt1 <- dt.raw %>% 
  arrange(query_artist, query_title, name, artist, -popularity) %>%
  distinct(query_artist, query_title, name, artist, .keep_all = T) %>%
  group_by(query_artist, query_title) %>%
  filter(n() == 1 | (n() > 1 & popularity > 0)) %>%
  ungroup()

# otherwise, pick the results manually
dt2 <- manual_dedupe_match(data = dt1,
                           id_cols.main = c("query_artist", "query_title"),
                           id_cols.matches = c("name", "artist", "popularity"))
