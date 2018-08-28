g <- read.table("~/Desktop/test.txt", sep="\t", quote="",stringsAsFactors=F)

chap <- 0
for (i in 1:nrow(g)) {
	if (g[i,1]=="WICOWOYAKE") {
		chap <- g[i,2]
	} else {
		n <- paste0("66",chap,g[i,1])
		cat(n,"\t",g[i,2],"\n",file = "~/Desktop/dakota.txt",append = T, sep = "")
	}
}