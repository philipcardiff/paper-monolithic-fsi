feel free to push back on any points below.

title

Should we change the title? the current title feels like it emphasises a JFNK method as opposed to a FV method.


abstract

"written in velocity, " the english does not seem right here - maybe "in velocity form" or "in terms or velocity"

remove bold text in abstract

Hron-Turek - should this be Turek-Hron since Turek is the first author?

"at density ratios of 0.1 and below, Dirichlet–Neumann coupling reaches its iteration cap in most cases."
should we say here "at density ratios of 0.1 and below, the partitioned Dirichlet–Neumann coupling reaches its iteration cap in most cases." => i.e. emphasise DN is partitioned in case a less informed reader is unaware; also, i guess our DN method was accelerated by IQN-ILS so it seems inconsistent with the rest of the abstract to say DN here but IQN-ILS later.

similarly, "IQN-ILS" is mentioned in the abstract without introduction, and noting it is partitioned DN acclerated by IQN-ILS approach.

"a flexible flag in air, which needs a reduced time step with either coupling, is reported as a limitation."
hmnnn... should this case be mentioned at all? maybe we should remove it.

The abstract notes that the monolithic method is slower than IQN-ILS in two cases (much slower in one), but it does not mention any cases where is is faster (or any "speedup" factors), which seems unbalanced and also leaves the reader with a skewed perspective on the method (i came away feeling like it was a very slow method, which is true in some cases but not in general, right?!).

"The implementation, built on solids4foam and PETSc, and all case set-ups are open source."
I think we need to be more explicit here than "open source" as codes can claim to be open source but author do not publicly share them (I know, it is not really open source then but I have seen this). In other papers, I have said something like the code and cases are open source and shared publicly with the community or something like that to remove doubt.


keywords

Should we add "OpenFOAM"?


introduction

I am not a fan of non-standard acronyms/abbreviations as they save little and risk introducing confusion. I wonder if we should avoid FV? For others, like FSI, JFNK, ALE, they may be more acceptable but we should review each one and see if an abbreviation is really needed at all.

"Weakly coupled (loosely coupled) schemes"
maybe "Weakly (loosely) coupled schemes"?

"(interface quasi-Newton with an approximation of the inverse Jacobian from a least-squares model) [29–33], reviewed by Delaiss´e et al. [34]" this looks strange - i dont think we need to make the distinciton that Delaisse reviewed the IQN-ILS method; maybe just say "... least-squares model) [29–34],"

"Dirichlet–Neumann iterations cannot converge for an incompressible fluid fully enclosed by ..."
this is a strong claim - are we should it is true? as opposed to DN methods struggle to converge in such cases?
Also, this statement suggests to me that we might consider adding such a test case to the paper to demonstrate/support this claim (also the Robin approach should still work in this case). I know Tukovic considered such a case in "Added mass partitioned fluid-structure interaction solver based on a Robin boundary condition for pressure, Zeljko Tukovi´c, Martina Bukaˇc, Philip Cardiff, Hrvoje Jasak, Alojz Ivankovi´c" although there may be more popular cases which are better references.

"Monolithic schemes avoid outer iterations and ..."
Here, we are (correctly) claiming monolithic schemes avoid outer fluid-solid iterations but the way it is phrased now may be misleading, since a reader may incorrectly think we are claiming there are no non-linear iterations which we would be untrue since in the current monolithic approach we have Newton iterations. So a reader may say you are just replacing fluid-solid outer iterations with Newton outer iterations - this misses a crucial point about how/where the nonlinearity is resolved but nonetheless we should consider rephrasing this sentence to avoid such confusion.

"Jaiman and Joshi [54] give a textbook account of the resulting algorithm, which the present method follows."
Is "which the present method follows" too strong a statement? Our current approach is certainly strongly inspired by Jaiman and Joshi although there are notable differences: FVM being the main one, but also we keep the nonlinearity in the resulting velocity-pressure system (fluid and solid) while Jaiman and Joshi linearise in time to a second order degree; there are also various other subtle (mostly FVM vs FEM related) differences.
This point also applies to the later "Relation to existing methods" paragraph.

"... is the closest in solver architecture" closest to what? I guess you mean to our proposed approach.
The introduction needs to be re-read with a closer look at avoiding such ambiguities.

The "flow" of the introduction text should be viewed and modified if needed.

"in a collocated scheme" I prefer using cell-centred throughout (maybe acknowledging collocated as a synonym when first used).

"a boundary condition that is adequate for a partitioned solver can limit the order of accuracy of the coupled solution;"
this sounds like we are saying that a 1st order boundary condition may be sufficient for 2nd order accuracy when used in a partitioned scheme but not in a monolithic scheme. Is that what we are saying?

For the paragraph which starts with "Three aspects of a monolithic cell-centred FV formulation are not settled by the finite element literature above.", I understand that this paragraph is meant to highlight research gaps, but I find it a bit confusing in terms of the three points that are made and/or the way they are presented. I understand each point but i came away from this paragraph unsure if these three points are meant to be take as gaps or something else. I think we should review the purpose of this paragraph and how that purpose is being achieved.

"used as the Jacobian, it gives only linear Newton convergence."
We show this as an alternative approach (which we dont recommend) - it feels like the way it is currently phrased is that our overall method gives only linear Newton convergence which is wrong. Revist this text.

"to the coupling of the ring." the english sounds wrong here, maybe "to the coupling of the ring case" or similar.

"... together with a comparison with a three-dimensional FSI experiment, ..."
this text is clunk as it uses "with a" twice in quick succession.

"... and a report of a case in which the method, like IQN-ILS, requires a smaller time step than that of the partitioned tutorial."
I dont understand this as it makes it sound like IQN-ILS is not a partitioned method when it is. review what is trying to be said here.

"... are released in solids4foam"
I think we should be explicit and say "are released publicly in solids4foam" and maybe even say something like i said in the first JFNK paper, i.e. "Thedescribedimplementationsareavailableinthe
solids4foamtoolboxforOpenFOAM,invitingthecommunitytoexplore,extendandcomparetheseprocedures."

10 sections seems like a lot. this may be ok but that is my immediate reaction when reading the end of the introduction.
also the short descriptions of each section seem to somewhat overlap such that a reader may not quite know the reson for each section.


governing equations

"with outward-facing unit normals ˆnF and ˆnS."
it is clear here that both normals are function of time t - i wonder if we need to note this explicitly at first since we do it for Omega and Gamma? Obviously it will be too verbose if used throughout but reviewers/academics do like to be tedious when it comes to consistency.
Actually, just after this we say "For notational compactness, the explicit time dependence of moving domains and boundaries is omitted where no ambiguity arises." which seems fine, although I guess we mean "from here on"? although, if so, then "(t)" should probably be added to the normals before this. I am not sure. Fig 1 caption uses n(t).

Fig 1 seems to be missing the deformed configuration row of images - it currently only shows the reference domain images

We use t0 for the reference configuration traction - we should double check there is no confusion/contraction with the rest of the paper as in the past i have used lowercase t for deformed configuration traction and maybe uppercase T for the reference configuration.

"For finite deformations, the solid is modelled as a Saint Venant–Kirchhoff material,"
Is this the only finite strain law we used? if so, that is fine, but check it. If it is true, then we should at least state the current approach is compatible with any standard finite strain law and in fact our implementation is already material law agnostic.

"half-cylinder, which Liu et al. [53] also model as linear elastic, and three-dimensional tube)"
it seems strange here to explicitly mention Liu et al - i would probably remove that reference here unless there is a strong reason to - i guess you put it here as the blob case actually does have finite strains and maybe you are just saying that we know that and are only assuming small strains for comparison with Liu.
By the way, I think the companion paper may have switched to a finite strain formulation for this case (neo Hookean I think).



