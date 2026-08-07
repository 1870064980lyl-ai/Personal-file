c
c Local-axial-stress feedback swelling for Abaqus/Explicit 2023.
c
c VUSDFLD properties:
c   props(1) = p_on   (MPa)
c   props(2) = p_stop (MPa)
c
c VUEXPAN properties:
c   props(1) = maximum free axial nominal swelling strain
c   props(2) = swelling response time tau (s)
c
c State variables:
c   SDV1 = local irreversible swelling fraction xi
c   SDV2 = local material-3 compressive stress (MPa)
c   SDV3 = axial-stress suppression factor g
c   SDV4 = achieved free axial swelling strain
c   SDV5 = equivalent pressure stress, diagnostic only (MPa)
c
      subroutine vusdfld(
c Read only -
     *   nblock, nstatev, nfieldv, nprops, ndir, nshr,
     *   jElemUid, kIntPt, kLayer, kSecPt,
     *   stepTime, totalTime, dt, cmname,
     *   coordMp, direct, T, charLength, props,
     *   stateOld,
c Write only -
     *   stateNew, field )
c
      include 'vaba_param.inc'
c
      dimension props(nprops),
     *          jElemUid(nblock), coordMp(nblock,*),
     *          direct(nblock,3,3), T(nblock,3,3),
     *          charLength(nblock),
     *          stateOld(nblock,nstatev),
     *          stateNew(nblock,nstatev),
     *          field(nblock,nfieldv)
      character*80 cmname
c
      parameter ( nrData=6 )
      character*3 cStress(maxblk*nrData), cPress(maxblk)
      dimension jStress(maxblk*nrData), stress(maxblk*nrData),
     *          jPress(maxblk), pressure(maxblk)
      parameter ( zero=0.d0, one=1.d0 )
c
      pOn = props(1)
      pStop = props(2)
      if (pStop .le. pOn) then
         call xplb_abqerr(-2,'VUSDFLD: p_stop must exceed p_on.',
     *        0,zero,' ')
         call xplb_exit
      end if
      if (ndir .lt. 3) then
         call xplb_abqerr(-2,'VUSDFLD: 3D stress state required.',
     *        0,zero,' ')
         call xplb_exit
      end if
c
c VGETVRM returns S11,S22,S33,S12,S23,S31.  For oriented solid
c materials these are corotational material components.  Components
c are packed with nblock entries per component.
c
      jStatus = 1
      call vgetvrm('S',stress,jStress,cStress,jStatus)
      if (jStatus .ne. 0) then
         call xplb_abqerr(-2,'VUSDFLD: VGETVRM S failed.',
     *        0,zero,' ')
         call xplb_exit
      end if
c
c PRESS is retained only to compare the new criterion with V06.
c
      jPressStatus = 1
      call vgetvrm('PRESS',pressure,jPress,cPress,jPressStatus)
      if (jPressStatus .ne. 0) then
         call xplb_abqerr(-2,'VUSDFLD: VGETVRM PRESS failed.',
     *        0,zero,' ')
         call xplb_exit
      end if
c
      do 100 k = 1,nblock
         do 20 j = 1,nstatev
            stateNew(k,j) = stateOld(k,j)
   20    continue
c
c Abaqus stress uses tension-positive sign; compression is -S33.
c
         s33Local = stress(k+2*nblock)
         pAxial = max(-s33Local,zero)
         pMean = max(pressure(k),zero)
         if (pAxial .le. pOn) then
            gAxial = one
         else if (pAxial .ge. pStop) then
            gAxial = zero
         else
            xPress = (pAxial-pOn)/(pStop-pOn)
            smooth = xPress*xPress*(3.d0-2.d0*xPress)
            gAxial = one-smooth
         end if
c
         field(k,1) = gAxial
         if (nfieldv .ge. 2) field(k,2) = pAxial
         if (nfieldv .ge. 3) field(k,3) = pMean
         if (nstatev .ge. 2) stateNew(k,2) = pAxial
         if (nstatev .ge. 3) stateNew(k,3) = gAxial
         if (nstatev .ge. 5) stateNew(k,5) = pMean
  100 continue
c
      return
      end
c
c ----------------------------------------------------------------------
c
      subroutine vuexpan(
c Read only -
     *   nblock, nDir, nShr, nExpanType,
     *   nElem, nIntPt, nLayer, nSectPt,
     *   stepTime, totalTime, dt, cmname,
     *   nstatev, nfieldv, nprops, props,
     *   tempOld, tempNew, fieldOld, fieldNew,
     *   stateOld,
c Write only -
     *   stateNew, strainThInc, dStrainTherDT )
c
      include 'vaba_param.inc'
c
      dimension strainThInc(nblock,nDir+nShr),
     *          dStrainTherDT(nblock,nDir+nShr),
     *          nElem(nblock), nIntPt(nblock),
     *          nLayer(nblock), nSectPt(nblock),
     *          props(nprops),
     *          tempOld(nblock), tempNew(nblock),
     *          fieldOld(nblock,nfieldv),
     *          fieldNew(nblock,nfieldv),
     *          stateOld(nblock,nstatev),
     *          stateNew(nblock,nstatev)
      character*80 cmname
      parameter ( zero=0.d0, one=1.d0 )
c
      epsMax = props(1)
      tau = props(2)
      if (tau .le. zero) then
         call xplb_abqerr(-2,'VUEXPAN: tau must be positive.',
     *        0,zero,' ')
         call xplb_exit
      end if
      if (nExpanType .ne. 2) then
         call xplb_abqerr(-2,'VUEXPAN: ORTHO expansion required.',
     *        0,zero,' ')
         call xplb_exit
      end if
c
      do 200 k = 1,nblock
         do 120 j = 1,nDir+nShr
            strainThInc(k,j) = zero
            dStrainTherDT(k,j) = zero
  120    continue
         do 140 j = 1,nstatev
            stateNew(k,j) = stateOld(k,j)
  140    continue
c
         xiOld = min(one,max(zero,stateOld(k,1)))
         wetNew = min(one,max(zero,tempNew(k)))
         gAxial = min(one,max(zero,fieldNew(k,1)))
         pAxial = zero
         if (nfieldv .ge. 2) pAxial = max(zero,fieldNew(k,2))
         pMean = zero
         if (nfieldv .ge. 3) pMean = max(zero,fieldNew(k,3))
c
         drive = max(zero,wetNew-xiOld)
         relax = one-dexp(-dt/tau)
         dXi = drive*relax*gAxial
         xiNew = min(one,xiOld+dXi)
c
c Pure axial swelling in local material direction 3.
c
         strainThInc(k,3) = epsMax*dXi
c
         if (nstatev .ge. 1) stateNew(k,1) = xiNew
         if (nstatev .ge. 2) stateNew(k,2) = pAxial
         if (nstatev .ge. 3) stateNew(k,3) = gAxial
         if (nstatev .ge. 4) stateNew(k,4) = epsMax*xiNew
         if (nstatev .ge. 5) stateNew(k,5) = pMean
  200 continue
c
      return
      end
