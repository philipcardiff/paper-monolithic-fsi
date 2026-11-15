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


comments above were pushed in 626ab41

In Eqs 15 and 16, t seems to be a true (deformed configuration) traction which is confusing witht he earlier definition of t in terms of initial configuration - see point above.



method

"The time step follows the quasi-monolithic formulation of Liu et al. [53] and Algorithm 2 of Jaiman and Joshi [54, Chapter 6]:"
See my notes above about the differences between our approach and the approach of Jaiman and Joshi.
I see that we do mention "in treating the convective term fully implicitly rather than linearising it about an extrapolated velocity" but we also treat the solid nonlinearly without a linearisation-in-time as Jaiman and Joshi do. I guess a reason we/I do this is that we "might as well" when using a JFNK approach.

"with Rhie–Chow-type pressure stabilisation"
if we use the higher order solid then i guess we use alpha stabilisation in those cases.

3.1 Finite-volume discretisation seems to be written entirely from a 2nd order perspective; we should check this section to ensure is consistent with any higher order solid we may use in some cases.

"Cell gradients are computed by a first-neighbour least-squares fit,"
If we are using leastSquaresS4f on tet grids then it uses point-cell neighbours in those cases.

"and an explicit non-orthogonal" => explicitly is misleading here as it is treated implicitly in time; "treated in a deferred correction manner" or similar is a better description.

"which keeps the implicit stencil compact." I am wary that "implicit" may be misleading here. Maybe "approximate Jaocbian" or similar would be clearer.

"when the time step is adapted" do we actually use adaptive time step in this work?

"on the first time step the backward scheme of OpenFOAM.com"
since reviewers are likely not from the OpenFOAM community, I wonder if we should phrase this as
"on the first time step the backward scheme (OpenFOAM.com variant)" or similar

"reverts to the Euler coefficients" should this be "reverts to the Euler (BDF1) coefficients"?

Are the n and n-1 time superscripts defined/noted somewhere?

Eq 25: "where vf is the face velocity interpolated linearly with a skewness correction," should this refer to \tilde{v}_f? as opposed to v_f?

"evaluated explicitly from the interpolated least-squares velocity gradient,"
see my comments above on the use of "explicit" and "implicit"

"as in the partitioned fluid solver of solids4foam." it seems strange to - out of nowhere - point out that this particular term is like the partitioned fluid solver of solids4foam; maybe remove this comment unless there is a clear reason for it.

"the convected velocity" we say we use linear of 2nd order upwind, but do we also use LUST somewhere in the paper? Please double-check.

"where vf is again this interpolated face velocity,"
please double check vf vs \tilde{v}_f and whether we are using the right one in each place.

"which was observed to damp transient flows"
a reader may wonder if we are referring to literature here or something we observed ourselves (but is not shown in the paper) or that we observed and demonstrated in the paper (e.g. case of appendix). we should make this clear, even if just saying that we noticed this in early tests.

Eq 31 uses uppercase T for the reference traction - see comments above.

"The cases of this paper use αd = 0.5 or 0.1 (Table B2)." double check this is correct.

"the geometrically nonlinear variant can instead use the high-order residual of Castrillo et al. [73]:"
we are using the high order residual of Batistic et al.: High-order cell-centred finite-volume solid mechanics using a
Jacobian-free Newton-Krylov method, Ivan Batistic, Pablo Castrillo, Philip Cardiﬀ.

"the displacement is reconstructed by a k-exact cubic least-squares fit "
solids4foam now has 3 higher order variants: in Batistic et al., it used the "moving least squares" variant (not k-exact approach) - double check which one we are actually using in the cases.

"the approximate Jacobian of the preconditioner keeps the compact linearisation"
should we saw "compact (low order) linearisation" here?

i see that we first mention higher order here but it feels like we should have briefly mentioned this somewhere at the start of the discretisation too.

"and the stress and point displacements are updated."
do we say how we calculate point displacements from the cell centred displacements?

" its sum over the steps telescopes, so the volume that crosses the wall relative to
the mesh stays of the order of ..."
I am not sure I understand what "telescopes" means here - maybe define what is meant or rephrase to make it clear.

Bottom of p15: "Measured after the start-up ...", it seems strange to list lots of numerical errors here for the various cases before the cases have even been introduced. maybe this can all just go in an appendix and we refer to that.

", as in the partitioned couplings of solids4foam."
once again, this comment seems out of place.

"and, where the weights of each fluid face sum to one, so does the total interface force; these are
identities of the transfer operator at the interface faces, and they do not by themselves imply
discrete conservation of momentum or energy by the complete discretisation, in which, for example,
the solid face velocity is reconstructed from cell values; the logged total interface force balances to
round-off (Section 4.4)"
this sentence (and text before this) is too long and difficult to follow.


Comments until the end of Section 3.3 are above

