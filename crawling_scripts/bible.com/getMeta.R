library(jsonlite)

getInfo <- function(nr) {
	
	url <- paste0("https://www.bible.com/de/versions/", nr)
	info <- fromJSON(paste0(url,".json"))
	
	url1 <- url
	url2 <- info$publisher$url[1]
	title <- info$title[1]
	local <- info$local_title[1]
	iso <- info$language$iso_639_3[1]
	name <- info$language$local_name[1]
	copy_S <- info$copyright_short$text[1]
	copy_L <- info$copyright_long$text[1]
	year <- grep("\\d{4}",copy_S,value = T)
	
	names <- c(  "# language_name:        "
				,"# closest ISO 639-3:    "
				,"# year_short:           "
				,"# year_long:            "
				,"# title:                "
				,"# URL:                  "
				,"# copyright_short:      "
				,"# copyright_long:       "
				)
	
	data <- c(name
			, iso
			, year
			, ""
			, paste0(local, "<br>", title)
			, paste0(url1, "<br>", url2)
			, copy_S
			, copy_L
			)
	
	return(paste(names, data))
	
}

writeBible <- function(file) {
	
	file_in <- "~/Desktop/crawl"
	file_out <- "~/Desktop/crawl2"
	
	nr <- strsplit(file, split = ".", fixed = T)[[1]][1]
	info <- getInfo(nr)
	iso <- substr(info[2], nchar(info[2])-2, nchar(info[2]))
	name <- file.path(file_out, paste0(iso, "-x-bible.txt"))
	n <- 2
	while (file.exists(name)) {
		name <- file.path(file_out, paste0(iso, "-x-bible-", n, ".txt"))
		n <- n+1
	}
	cat(info, file = name, sep = "\n")
	
	text <- file.path(file_in, file)
	
	cmd <- paste("cat", text, ">>", name)
	system(cmd)
	
}

texts <- list.files("~/Desktop/crawl")
sapply(texts, writeBible)
