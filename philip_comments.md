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

Comments below are on the paper at commit cf30173 from Section 3.3 onwards

"using the cell-centred velocity gradient, vS,P + (xf−xP)·(∇0vS)P; using the cell-centre value directly would give a
first-order interface velocity."
The English seems a bit clunky as it uses "using the" twice in a row

"and the interface acceleration is the BDF2 difference (with the time scheme of the fluid velocity) of the interface velocity in Equation (34)"
I find it hard to follow the English of this clause.

"The interface pressure, which gives the solid traction, is then extrapolated from the adjacent cell using this gradient."
This sounds like the solid traction comes entirely from fluid pressure (without viscous stresses); this should be clearer.
Also, here, the point is that Eq 35 is used to extrapolate the pressure to the fluid interface - i think this point is not sufficiently emphasised or made clear - maybe just put "(Eq 35)" after "this gradient".

Several sentences start with the word "Because": we should avoid this.

"this is the boundary-face form of the diffusion term in Equation (25), which has no non-orthogonal correction on boundary faces."
Why do we neglect non-orthogonal correction here? I think this expression may still be 2nd order if grad(v) at the cell centre P is used. I am not suggesting we re-run all cases but this may warrant an investigation and potentially a comment or note here (and maybe a proposed improvement in solids4foam via an issue). Actually, the tangential gradient at the wall is already effectively calculated via Eq 37 in the q term - it seems like a similar construct could be used to correct the normal viscous term. Having said all of this, it seems that we already get 2nd order behaviour, although this may be because our near-wall mesh becomes orthogonal in the limit of mesh refinement.

In Eq 18, we use "\outer" for an outer product between vectors, but in Eq 37 we do not use \outer between the two n vectors - we need to check all equations use one consistent notation for outer products between vectors (and other vector-tensor operations); i probably prefer to keep the \outer but I am happy to follow the common conventions.

In Eq 37, there is a "G dot n": should this be "n dot G" per OpenFOAM convention? Check the code.

"and the normal derivative of the normal velocity is taken from continuity"
Can we be clearer here? Is there an expression we can give or refer to?

"The same value enters the wall flux of the transpose term in the momentum residual,"
I am a bit unclear here - are we saying that all internal cells/faces also use some form of Eq 37 - I dont think so but this sentence is confusing me.

"Because εf is the discrete rate of the prediction error, its contributions from
successive steps cancel except for the most recent ones, so the volume that crosses the wall relative
to the mesh stays of the order of the current prediction error and does not accumulate"
I dont actually understand this argument - maybe the text is fine, but if there is an easy way to help me understand, it would be good, e.g. maybe additional sentences explaining it in a different way.

"Setting the relative flux in the convective term to zero on the interface omits εfvf, which is of the same
order."
Are we saying this as a hypothetical (i.e. are we saying "if we set ...") or is this what we actually do? This is unclear to me in the current text.

"Optionally, a conservative transfer distributes the fluid face forces to the solid faces with the transpose of the velocity transfer in Equation (38),"
Here I am a but unsure of how this is different from Eq 38 - the only difference I can see is that we interpolate force instead of traction - I am not sure where the "transpose of the velocity transfer" appears. Maybe the text is fine or maybe it can be clearer but either way I need to understand this better. This is related with the subsequent explanation about power balancing.

"For the geometrically nonlinear solid, this requires the interface traction to be applied on the undeformed area"
This sounds like a limitation but i think it is not - i suspect we are just saying this is required in the implementation; but this could be clearer.

"The other non-conformal interfaces, those of Turek–Hron FSI3,
the Hessenthaler flap and the walls of the collapsible-channel order study of Section 7.3, use AMI
with traction interpolation"
A reader might wonder why we use conservative interpolation is some cases and not in the others - in fact, why do we?
I am not suggesting we re-run cases but some brief explanation is needed. Also, a reader may wonder if we compared then which we did - although I am not sure if it is shown in the paper (or an appendix - which may be more appropriate).

"The displacement that moves the fluid mesh (Section 3.6) is transferred with the same face
weights for the face values and with the point transfer of the interface mapping for the mesh points."
I am really struggling to understand this sentence.

"and a step length sk"
Is sk really a step length? Is that standard terminology? To me, ∆Uk already contains a length (and a direction) while sk is like a damping or under-relaxation factor.

"with the default differencing parameter of PETSc"
double check we definitely use the default scaling in every case as I vaguely remember us trying different perturbations when debugging convergence.

"Used as the Newton operator itself,"
Is this self-explanatory? Do we need to explicitly say that we mean if a non-Jacobian-free approach is used?
I am wary that the reader may not understand what we mean.

"By default sS is the average over the solid cells of 1/(µS∆t), evaluated once with the initial time step and not updated
when the time step is adapted, and sF = 1; sF = 10^8 in all the cases of this work."
This sounds like we are saying that the default value of sF in solids4foam is 1 but this is an irrelevant (and confusing) detail, in particular if we actually use 10^8 everywhere in the current work. It would be better to just say what we use in the current work. Separately, if 10^8 is what we used for all cases then it seems like it should be the default - i suggest we make a solids4foam issue for this, which may also note that the effect of this scaling needs more examination.
Back to the paper, a reader may wonder where the 10^8 value comes from - i suspect it is linked in some way to the ratio of stiffness between the solid and fluid approximately - but as I said this may not be optimised and may warrant more investigation for solids4foam (but maybe not in the paper if cases seem to work).

"The solid factor sS takes its default value in every case."
Once again, the reader does not care about the defaults in solids4foam - just say what we used in this work.

Fig 2: the fluid pressure block says it uses "BoomerAMG" while the solid block says "direct (LU) or AMG": we should be consistent and say BoomerAMG or AMG not mix both.
Related to this, Fig 2 is great but it introduces several PETSc-specific terms which someone unfamilar with PETSc would be confused by - our options are (a) to define these in the caption or (b) express them in a non-PETSc way, or (c) use approach (b) but also in brackets mention the PETSc-specific term names so people can track the actual option used.

3.5.1 Field-split preconditioner

"The tutorial settings use ..."
The reader does not care about solids4foam tutorials or their settings => descriptions should focus on the work in the paper and options we have used. But it is fine to state the relative merits of the two solids preconditioner options - you may even point the reader to Cardiff et al. [61] which examined this in detail.
Also, double check we actually do use the "redundant" option in all cases in Sections 4-6 as opposed to block Jacobi + LU - and also check the boomerAMG cases are correct.


3.6 Fluid mesh motion

"These constant-step coefficients are used also when the time step is adapted, so the prediction
is then not second-order accurate;"
I think it is a bad idea to refer to options not explored in this work. In fact, maybe we should just not mention adaptive time steps at all since we dont use them here (check earlier where we also mention them).

"The campaign build (Section 4.1) instead ..."
I dont think we should talk about campaign builds - instead, stick the methods description - if we tried two methods, then fine we can describe both and note their merits and comment on any tests we performed.
Also, here I am confused as to which method we actually used in the paper.
And for "and the order-3 FSI3 errors on the level-1 flag by less than 0.01%." I dont even know what "order-3" means - and am wondering if mentioning these errors here make sense - maybe it does.

"with a solid model of solids4foam used as the mesh motion solver"
I dont really like the way this is stated, since up to this point, we have not mentioned any solids4foam code/class names.

Is the mesh motion method correct here? In our latest code, I dont think we store the initial fluid mesh - maybe the current description is correct but please check it.

"a total Lagrangian neo-Hookean pseudo-solid for the cavity and the half-cylinder; and a total Lagrangian hyperelastic pseudo-solid weighted by δ for the collapsible channel"
why are we saying both "a total Lagrangian neo-Hookean pseudo-solid" and "a total Lagrangian hyperelastic pseudo-solid" as neo-Hookean is hyperelastic too and this sounds like we have a different hyperelastic law (if so state it).
Also, we introduce the linear elastic pseudo solid but just say we also use a TL form without even saying anythign about it - at least, we should note that it is like Eq 48 but TL form.

"On the refined Turek–Hron meshes of Section 6.1, the partitioned couplings accept only a pseudo-solid assembled on the current mesh"
This sounds like a limitation of our implementation or tutorial setup => describe in terms of what methods we used.

"starts from a second-order Taylor extrapolation of the mesh displacement rather "
extrapolated from where to where? this is unclear.

"with q= 1 or 2 and, by default, cmin = 0.1 and cmax = 100;"
once again, state what we used - not what solids4foam uses as a default

I am not sure all of these case-specific details should appear in this section since we have yet to introduce the cases. Would it make more sense to define the options used in the cases themselves? I am not sure what would be clearest.

"but the coupled solve currently requires every process to own fluid cells,"
Is this true? If so, it is a bug of our current implementation and an issue should be filed.
Eitherway, this need not be mentioned here - I wonder if the resulting chosen decomposition strategy explains less than ideal scaling in some of our cases.

"the two-dimensional runs decompose the regions independently with the method of the tutorial"
do not refer to solids4foam tutorials - describe what is done in this work.

Algorithm 1 has "(for a possible retry)." but we do not describe or demonstrate retries in this work - i suggest we remove this. Lines 7-14 describe the same retry method but we do not describe or demonstrate it - we should remove this from the paper.

4 Verification and consistency

"Sections 4 to 7 assess the method on the cases of Table 1 under the common protocol of Section 4.1."
It seems strange to introduce sections 4-7 from within section 4; as in, it feels like this introduction should be outside section 4 - having said that, I am not sure how else we would do it - we could make 4-7 as subsections of one large section 4 but i dont think that is nice either. so maybe it is fine. just my thoughts.

Table 1: should we addd a citation beside oomph-lib and FeatFlow. Similarly we should cite them both when first mentioned in the text.
"partitioned" vs "partitioned, same meshes" vs "partitioned, same levels" - are these all the same? It is not clear to me (or presumably a reader) how they differ.

"campaign build v2.2-1808,"
I am not sure where this code comes from but the "v2.2" could confusingly suggest we are using v2.2 of solids4foam as opposed to a derivative of v2.4. But ok we will fix all of this before submission.

"The half-cylinder runs of Section 6.2 use a later build of the same branch (2935daa53)"
we should double check this is actually true - as in, do we actually use a different build.

Give a citation for Meluxina.

"stalls on the shared file system make it 11–39% larger and spread it by up to 34% between repeats"
Hmnn, can we re-run these cases? Surely stalls are uncommon and we can avoid such a statement with a rerun.

"The mesh study of Section 6.2 was run on a workstation,"
Why do we not give CPU details for this workstation whereas we give CPU details for Melxuina?

"or timed out" what does that mean here? does it mean it ran out of slum queue time? if so, a reader will just say run it again and increase the time!

4.2 Ring added-mass problem

Is it confusing that we use mu for added mass? and also for shear modulus (or maybe we have a subscript there)

Why did we pick "µ= 0.101, 1.008 and 10.08" as opposed to 0.1, 1.0 and 10? They seem like strange numbers.

"The wet frequency error, the wet/dry ratio error, the amplitude loss per period and
iteration counts; IQN-ILS and Robin–Neumann are run on the same meshes and steps for the
iteration counts and timings."
The English does not seem correct here - it seems like it is half finished notes.

"within 0.004 percentage points at every time step "
Why do we say "percentage points" here but just use "%" just before this?
Also, this sentence is very long with many clauses - consider breaking it up and making it easier to read.

Table 2: what does "one process." mean in the caption? does this mean run in serial? If so, say that and maybe "one process" in brackets or something like that.


4.3 Pulsatile compliant tube

"the pimpleFluid option fluxConsistentPatches" I am not sure we should mention this solids4foam-specific option here.

Table 3: it seems strange/wrong to mention "(build 1252bd2e5)" here.

"The timings of these runs were taken on a shared node and are not reported."
Would it be expensive to generate true timings here?
Based on the iterations, it seems like the monolithic approach will be faster.


Comments up to just before section "4.4 Effect of the interface treatment"


4.4 Effect of the interface treatment

"Two ingredients of the interface treatment of Section 3.3 can be switched by an option"
This seems like a very software/implementation centric way of saying it - since we are submitting to a numerics journal, i think it is better to present things from a numerical methods perspective, i.e. two approaches for XXX were described and here we compared them, or something like that.

"The interface pressure treatment thus controls the damping ..."
Is "controls" the right word here? it seems like "strongly influences" or similar would be more appropriate

"and arises because the linear-geometry solid integrates the traction over its undeformed face areas and
the fluid over the deformed faces"
I think this might should be made clearer -> when we assume linear geometry, we do not move the solid mesh but we do move the fluid mesh hence their is a geometric discrepancy. I wonder then if comparing the conservative and non-conservative approaches here is fair sinec the conservative is fully correct even for the non-moving linear geometry solid. It may be fine the way it is but this is worth another look.

"Two further ingredients cannot be switched off in the released code,"
I would remove this entire paragraph since it refers to old versions of our code. If we were to say anything like this, it should be from the numerics perspective and to shareo our learnings, e.g. Although not shown here, during the preliminary development phase, two additional ingredients were found to be important ...

"The quasi-monolithic and partitioned couplings in solids4foam solve the same continuum problem with different fluid solvers"
Rephrase this from a numerical methods perspective, not a solids4foam one, i.e. in the proposed monolithic approach, the fluid solver is essentially a coupled solve while in the partitioned FSI cases the fluid solve is based on PIMPLE - it is fine to mention the specific solids4foam classes/models as an aside (e.g. in brackets) but not as the primary point.
Check the entire text for similar constructs.

"One difference did not."
This paragraph should be remove since this problem has now been fixed in the monolithic solver, right?
Also, it is clearly inappropriate to refer to a solids4foam PR in a numerics paper.

Table 4
- the says we are using a gradient limiter in some cases, and, generally different schemes from partitioned for some cases - double check this? Is there a reason for this? Ideally we would use the same schemes insofar as possible.
- "O(h2 ) on smooth meshes, lower near the cavity plate corners" is this a difference? I am unclear if this is a comment on both or one of the approaches - it does not seem like a difference as the column title suggests; similarly many other entries in this column do not clearly seem to be differences and it is unclear to me if the comments are referring to the monolithic or partitioned schemes.
- "Interface pressure" a reader will ask why we are not also using "fixed gradient from the momentum equation" for our partitioned solver - I am also wondering that
- mesh motion - a reader will ask why not use the same mesh motion for monolithic and partitioned? which is fair - our answer is likely because our monolithic was initially limited/hard-coded to one scheme but now both our monolithic and partitioned allow general choices. I am not suggesting we re-run cases but the text should be clear about any apparent arbitrary differences in schemes. 
- the spacing between rows seems too small making it difficult to see where a new row starts


4.5.2 Channel flow over a cavity with a flexible bottom

"The flow is at Re= 100"
When stating Re we need to say with respect to what length scale, e.g. inlet channel height or something else.

"as in the partitioned tutorial,"
Do not refer to solids4foam tutorials => this is a numerical methods paper and we should only refer to test cases as described. Check and fix all occurances in the paper

"Aitken under the strict convergence test."
I do not see where "strict convergence test" was defined

In the "Measured." subsection (in this test case and others), the English seems broken: the sentences seem like incomplete notes. Fix these and check the same for all "measured" subsections.

"Further runs on levels 2, 3 and 4 use the partitioned solver’s face interpolation (linear rather than skewness-corrected linear) for the quasi-monolithic continuity flux, the leading candidate among these differences for the remaining difference."
Generally, we do not need to state the journey we went on to reach the results shown, i.e. if earlier parameter choices has issues and later replaced with better ones, then we can just state the final "good" ones that we used -> we dont need to give a running story of everything we tried.
If, here, we are aiming to show the difference between these two options (linear and skew corrected) then ok make it clear that that is what we are doing; also, I dont think we properly (or at all) described skew corrected in the methods and this should be briefly explained.

it is fine that we used Aitkens here but a reader may wonder why not use IQN-ILS or Robin - we can probably add a note that both could be used here (and are probably faster), but will give the same partitioned solution assuming iteration errors are small.

Table 5: it is unclear what "cost" refers to here - it seems to be the ratio of iterations but that is not the same as "time to solution" cost - whatever it is, it should be clarified in the caption and text.
Also proponents of IQN-ILS may argue that it will allow less iterations on a case like this.

"so the skewness-corrected interpolation causes the slowly decreasing difference,"
a reader may ask why we are not using this same scheme for both, i.e. if partitioned uses skewness corrected then monolithic should too then there is no need to discuss this effect (it is hardly suprising there is a difference is a different interpolation is used). If we are trying to show skew corrected is more accurate on this case, then that is a different point. We need to sort this out in this tet case and decide what we are trying to show.

"even so, it costs 1.7 to 2.8 times as much as Aitken to reach steady state,"
We need to make the stopping criteria clear - is it a fixed total time or something else. also, did we introduce physical damping for the solid here?
also, if Aitken uses Euler for the solid while QM uses BDF2 then this could explain why Aitken reaches steady state faster.
Once again, we should be clear what we are actually comparing.

"In the womersleyTube problem"
Do not use solids4foam camelCase tutorial names => give the actual case name in our paper.

4.5.3 Pulsatile compliant tube

"so the uncorrected traction would leave a difference that does not vanish under refinement."
What "uncorrected traction"? this is unclear. Be explicit what you are referring to.

"Before the correction the wall-displacement phase ..."
What correction? If this - once again - refers to some prior initial development then do we need to mention it at all?
If we want to show an effect of a method choice then fine make that clear.


5 Robustness

"Both use BDF2 in both regions"
using "both" twice in quick succession seems clunky

Fig 12: before this, we have claimed/stated thata partitioned schemes struggle with large added mass, but these results suggest that statement is somewhat of an exaggeration. I mean, yes, we can see the number of iterations increase for the partitioned schemes as added mass increases (e.g. they might double) but generally they still seem to work well, e.g. IQN-ILS works for all and only needs 6 iterations. We dont need to change anything per se, but a reader may question the strength of some of our repeated claims about weaknesses of partitioned schemes when they see these results. Ah wait, the "Collapsible channel" case shows large differences between partitioned and QM and really does show partitioned schemes struggling as we claimed => maybe we need to add a comment to the end of the 5.1 section to preempt any reader comments like my one above (where I had yet to view the "Collapsible channel" results) - I guess the ring problem is a bit easy even if it has high added mass.

"at a Reynolds number of 50"
with respect to what is Re calculated? also, be consistent => Re or Reynolds number

"to be well posed for a continuum solid."
We should state clearly what changes we made to make it well posed and hence why it was not well posed before, rather than assuming the reader already knows.

"oomph-lib" add citation for oomph-lib

"At ∆t = 0.00625 s the quasi-monolithic trough
on this mesh lies 0.71% from oomph-lib, against 1.17% with the conformal 320 ×8 solid on the
finer fluid level 4."
this sounds like the difference increases with mesh motion, but checking back i see that this is a coarser solid mesh => we should make this easier for the reader to follow

Fig 14 is not great: the limits of the pressure and velocity scales are poorly chosen as both fields are almost entirely blue. also the velocity streamlines look strange as they do not fill the downstream channel - it may be better to remove the streamlines entirely or consider a different visualisation.

"percentage points"
once again, why are we sometimes saying "percentage points" and sometimes %? Surely using % is cleaner and more consistent and more common.

"Mesh motion."
this subsection refers to a prior failure that we subsequently resolved. At most, we should just make a note about it, e.g. helping readers developing their own codes.

"in the flag of Section 7.1,"
I still need to review 7.1 but I suspect we will cut it, so we may need to make the point about smaller time steps being needed for some cases in a more general way or by referring to a different case.

"The robustness of the partitioned couplings depends on settings such as the Robin coefficient and
the IQN-ILS history, here those of the companion paper"
The English seems wrong here - the sentence seems incomplete.

" the maps do not measure
how far other settings would extend it"
What does this mean? I guess you are trying to say that maybe IQN-ILS, for example, would do better here if its free parameters were optimised, and similarly for the Robin scheme. This should be made clearer.

6 Accuracy, cost and parallel performance

"Both couplings are run on one family of three unstructured fluid meshes,"
If we used Gmsh here, we should mention it and cite it.

"where the jump stabilisation of Section 7.3 "
it seems trange to be referring to a future section here, without a clear reason that i can see.

For the Turek Hron case, do we need to make it clear that we used the same post-processing extraction process on the FeatFlow results as opposed to using the actual reference values defined in the Turek Hron paper, e.g. I think they quote the values from the last cycle of a t = 20 s run as the references. We should make it clear what we are comparing.

"the flag is geometrically nonlinear, for which the velocity and displacement solids are not algebraically
equivalent in time,"
this makes it sound like there is an inconsistency between them but i guess we are just saying the differences comes from the time schemes and these should reduce with reducing time step, right? We should make this clearer.

"on this mesh family neither coupling shows the first-order sequence of
the companion paper’s meshes, so that sequence comes from the discretisation and meshes rather
than from the coupling."
What? What 1st order sequence are you referring to? a reader will be very confused as they will likely not have read the companion paper. Also, if the campanion paper has a 1st order issue then it should fix it, e.g. use our meshes or fixes.

"One Newton iteration therefore costs as ..."
This sentence seems to long which makes it hard to follow

Cost: it is clear that the monolithic coupling convergence is good in the sense that it takes only 2 Newton iterations - but it is slower than the partitioned. It seems that this slowness primarily comes from the coupled fluid solver it uses in contrast to the more efficient PIMPLE fluid solver of the partitioned scheme, e.g. if the partitioned FSI scheme was forced to use newtonIcoFluid, I guess we may see it slow down in the same way. I think it would be insightful to add some comments on this, and possibly run a coarse mesh test (partitioned with newtonIcoFluid to support the discussion). I imagine a take-away from the paper might be that targetting the fluid solver speedup would be a good strategy to accelerate the monolithic solver. Literature suggests using a PIMPLE preconditioner for the fluid solver although my initial tests with this did not show useful speedups but it will be worth revisiting after this paper is submitted - we could even note this in future work.


6.2 Elastic half-cylinder in a viscous channel flow

"Reynolds number" with respect to what?

"on the tutorial mesh" do no refer to tutorials

"Both couplings use the same development version, later than that of most other results"
how important is this to note in the paper - as opposed to note in the shared code/cases? i feel like it does not need to be mentioned here.

Once again, for IQN-ILS, we may need to caveat the cost with the fact that we did not use coupling interface information in IQN-ILS which generally reduces the number of iterations and cost.

"Mesh convergence." some content in this subsection seems to repeat content from the prior subsection e.g. in terms of accuracy and time.
we should not repeat things (unless we are making some new point where the repetition facilitates reading)

Fig 21 is a nice image - i wonder if adding small velocity vectors in the fluid would enhance it (showing local flow direction) - it is worth a try.

6.3 A three-dimensional experiment: the Hessenthaler flap

"Re= 1283" with respect to what reference length?

Mesh: we should state that we used cfMesh here and cite it. Similarly, check all other cases and say how we generated the meshes and add citations if external tools like cfMesh and Gmsh are used.

"and all three pass the strict mesh checks."
I suggest we remove this or clarify mesh quality metrics as it is unclear what this means.

"Both couplings use second-order backward time integration"
previously we have said BDF2 => be consistent throughout the paper

"rF0–rF2"
Do not use our internal naming conventions here => be consistent with other cases in the paper, e.g. level 1, 2, 3.

"The partitioned runs use a different solids4foam build from the quasi-monolithic runs, which
include the interface correction of Section 3.6."
I dont think we should refer to different builds like that here (it is ok for shared code/cases); instead, we just need to note the methods used or ensure they are clear.


Fig. 23: the bottom images (velocity profiles c and d) show a lagged profile for the models presumably because we are averaging over the MRI voxel sizes - we should double check we using using the correct voxel size and averaging approach here.
in fact, in hessenthaler they state that numerical experiments showed that the velocities and their corresponding volume averages were sufficiently similar that comparisons between pointwise numerical results and volume-averaged MRI data were expected to be valid. Also they used an MIR with an in-plane voxel size of 1.302 mm and a slice thickness (presumably axial direction) of 6 mm. So we should check we are averaging our results over the correct voxel size (it should be 1.302 mm) but also i think it would be valuable to plot our actual pointwise velocity in a figure like this especially since hessenthaler shows it should be defensible. Our piecewise averaged model velocity profile looks very coarse and presumably very different than our pointwise values which makes me suspicious of our averaging. I think this may explain why our results apparently underpredict the experiment velocities.
Also, we need to replace rF0/etc with consistent mesh level names, e.g. level 1, etc, as noted above.

"three in 2, 1 and 22 steps of the first 5 s on rF0–rF2)"
I do not understand the English here

"this is a property of the convergence"
future work (and a solids4foam issue) should fix this => i think we already have an issue for this.

"The voxel-averaged velocities differ from the MRI velocities by 5% of the inlet peak on average,"
What is the "The voxel-averaged velocities"? Averaged across where? inlet/outlet/somewhere else? make this clear.

"which is consistent with, though not proven
to be caused by, the single-level ILU(0) preconditioning of the velocity block while IQN-ILS needs
about four coupling iterations on both meshes;"
the way this is phrased will make a reader/reviewer ask "well, did you try changing ILU(0)?"
If we really believe this to be true then we should really check it; however, these cases are costly so another option is we rephrase this in a way to say that we did not optimise the monolithic linear solver settings for this 3D case and the ILU(0) may be the reason for the poorer scaling and this is something we will look at in future work. If we go this way, I suggest we add an issue to solids4foam aimed at optimising the monolithic solvers settings for 3D cases like this.

We should be careful with our conclusions from this case - currently they seem a bit strong in the way they are saying partitioned is faster without appropriate caveats on the monolithic linear solver settings. That is, it is credible that the monolithic solver could be competitive in this case with better linear solver (presumably preconditioning) settings and the actual monolithic scheme itself is good (e.g. Newton converges in very few iterations).

6.4 A three-dimensional tube: consistency, performance and scaling

Fig 26 caption: do not refer to "tutorials" as noted above.

"so the quasi-monolithic runs use tutorial meshes with the wall arcs placed exactly
on both sides (solids4foam PR #625)"
do not refer to solids4foam PRs as noted above

"the companion paper’s Robin–Neumann runs predate that
change and use AMI interpolation across a wall mismatch of up to about 1 µm"
do not refer to old builds etc - just describe the methods. If the Robin models use different meshes then we state this or consider rerunning with the same meshes => actually we did this so we should remove all references to the old Robin meshes since they add no value and only add confusion.

"Against the original companion-paper meshes the level-3 difference was"
The companion paper should probably also just use the corrected meshes and not refer to the old meshes.
Of course, we can still note the importance of setting up the mesh in the correct way and maybe even say our initial study found larger errors were introduced by note correctly setting up the meshes in this way.

"the verification driver’s axis pressure probes lie on ..."
rephrase this as a helpful note on result extraction where we need to be careful about where the extraction happens - rather than phrasing it in terms of a "verification dirver"

"File-system stalls ..."
Do we really need to present results with system stalls? Cant we rerun any affected cases so we can avoid this? where at most we just add a note about being careful to look out for and avoid such stalls when comparing times.

"and the coupled solve does not proceed when a process owns no fluid cells "
as noted above, do not refer to this simple implementation limitation => anyway i think this may be fixed or there is an issue to fix it.

6.4.3 Effect of the preconditioner and Jacobian settings

"Discussion: parallel cost of the coupled solve."
this subsection is very small and i am not so clear on what it is adding. Check this again and see if it needs rephrasing or moving to the subsection above or removing.

6.5 Cost per step and number of iterations

this section reads well but I think we should add caveats at the bottom that are conclusions here are based on the chosen partitioned parameters (e.g. coupleReuse in IQN-ILS) and monolithic linear solver/preconditioner settings.

7 Limitations - I am not sure this section adds value - see my comments below - I am thinking we remove it, and any limitations could instead just briefly be noted near the end of the conclusions section, naturally linked with future work.

7.1 Time-step limit in a three-dimensional flag

Newton methods are well known to fail with large time step when nonlinearity is strong and continuation is not used. This is a sentence at most. In addition, we should not introduce a new test case in a limitation section.
This is a cool test case but is not needed or useful for this paper so we can remove it.

7.2 Solid block of the preconditioner

We have already well discussed this redundant LU solid => anyway this is just a user choice and we used AMG in some cases and if we liked we could have used bjacobi LU => i do not see any value in this section. Once again, this is a sentence at most.

7.3 Velocity solid on thin structures

Are you sure we did not already use the high order solid in this paper?
Once again, it seems strange to introduce new results in a limitations section.
it seems more appropriate - if at all - to note these results in the cases in question, possibly referring to an appendix.
Ideally, at least one test case in the paper would use the higher order solid for both partitioned and monolithic approaches as a demonstration just to show it works (but the scheme is still second order) => maybe using some results here as a follow on subsection in one or both cases, using appendices as needed.

7.4 Fluid mesh motion

This has already been discussed as far as I can see => I dont see the added value.

7.5 Software - why does this section appear under "limitations"? this does not seem right. also i am not sure this section adds much value - anything of value here could be mentioned elsewhere, e.g. in the methods when we say implemented everything in solidsfoam.


8 Conclusions

"main extensions" - a higher order fluid is on our roadmap so we can note this -> we are aiming to create truly higher order FSI solvers - both monolithic and partitioned - so higher order solid, fluid and interface transfer.

"possibly with overset meshes" - we should also mention immersed boundary methods here - I would cite the immersed boundary Turek Hron tutorial in solids4foam if possible so readers can see we already have the basic method established.

All appendices need to be double checked for correctness and clarity.
