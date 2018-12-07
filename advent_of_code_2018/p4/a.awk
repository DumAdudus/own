/Guard/{g=$7}
/falls/{s=$3}
/wakes/{
    for(t=s; t<$3; ++t) {
        ++zg[g];
        ++zgt[g","t]
    }
}
END{
    for(g in zg)
        if(zg[g] > zg[og])
            og=g;
    for(t=0; t<60; ++t)
        if(zgt[og","t] > zgt[og","ot])
            ot=t;
    print og, ot, og*ot
}
