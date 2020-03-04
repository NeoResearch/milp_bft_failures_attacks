<?xml version = "1.0" encoding="UTF-8" standalone="yes"?>
<CPLEXSolution version="1.2">
 <header
   problemName="n4.lp"
   solutionName="incumbent"
   solutionIndex="-1"
   objectiveValue="2"
   solutionTypeValue="3"
   solutionTypeString="primal"
   solutionStatusValue="101"
   solutionStatusString="integer optimal solution"
   solutionMethodString="mip"
   primalFeasible="1"
   dualFeasible="1"
   MIPNodes="5399"
   MIPIterations="60723"
   writeLevel="1"/>
 <quality
   epInt="1.0000000000000001e-05"
   epRHS="9.9999999999999995e-07"
   maxIntInfeas="0"
   maxPrimalInfeas="1.1102230246251565e-15"
   maxX="40"
   maxSlack="40"/>
 <linearConstraints>
  <constraint name="initializeSendPrepareReq(1,1)" index="0" slack="-0"/>
  <constraint name="initializeSendPrepareResp(1,1)" index="16" slack="-0"/>
  <constraint name="initializeSendChangeView(1,1)" index="32" slack="-0"/>
  <constraint name="initializeRecvPrepareReq(1,1,1)" index="48" slack="-0"/>
  <constraint name="initializeRecvPrepareResp(1,1,1)" index="112" slack="-0"/>
  <constraint name="initializeRecvCV(1,1,1)" index="176" slack="-0"/>
  <constraint name="initializeBlockRelay(1,1)" index="240" slack="-0"/>
  <constraint name="singlePrimaryEveryView(1)" index="256" slack="0"/>
  <constraint name="primaryOnlyOnce(1)" index="260" slack="0"/>
  <constraint name="prepReqOnlyOnce(1,1)" index="264" slack="-0"/>
  <constraint name="prepReqReceivedWhenSelfSended(1,1,1)" index="280" slack="-0"/>
  <constraint name="prepReqReceivedSendByJ(1,1,2,1)" index="440" slack="-0"/>
  <constraint name="prepReqReceivedOnlyOnce(1,1,1)" index="920" slack="1"/>
  <constraint name="sendPrepReqOnlyIfBlockNotRelayed(1,2)" index="984" slack="0"/>
  <constraint name="sendPrepReqOnlyIfViewBeforeWasAccomplished(1,2)" index="996" slack="-9.9920072216264089e-16"/>
  <constraint name="prepRespQuicklySendIfHonest(2,1,1)" index="1008" slack="-0"/>
  <constraint name="prepRespSendOrNotIfYouAreByzantine(2,1,1)" index="1116" slack="-0"/>
  <constraint name="sendPrepResponseOnlyOnce(1,1)" index="1260" slack="0"/>
  <constraint name="prepRespReceivedWhenSelfSended(2,1,1)" index="1276" slack="-0"/>
  <constraint name="prepRespReceivedSendByJ(2,1,2,1)" index="1420" slack="-0"/>
  <constraint name="receivedPrepResponseOnlyOnce(1,1,1)" index="1852" slack="0"/>
  <constraint name="sendPrepResponseOnlyIfBlockNotRelayed(1,2)" index="1916" slack="0"/>
  <constraint name="sendPrepResponseOnlyIfViewBeforeWasAccomplished(1,2)" index="1928" slack="-1.1102230246251565e-15"/>
  <constraint name="blockRelayIfEnoughPrepResp(2,1,1)" index="1940" slack="-0"/>
  <constraint name="blockRelayOnlyOncePerView(1,1)" index="2084" slack="1"/>
  <constraint name="blockRelayLimitToOneForNonByz(1)" index="2100" slack="1"/>
  <constraint name="sendCVOnlyOnce(1,1)" index="2104" slack="0"/>
  <constraint name="changeViewReceivedWhenSelfSended(2,1,1)" index="2120" slack="-0"/>
  <constraint name="receivedCV(2,1,2,1)" index="2264" slack="-0"/>
  <constraint name="receivedChangeViewOnlyOnce(1,1,1)" index="2696" slack="0"/>
  <constraint name="nextPrimaryOnlyIfEnoughChangeView(1,2)" index="2760" slack="-9.9920072216264089e-16"/>
  <constraint name="nextPrimaryOnlyIfPreviousPrimary(1,2)" index="2772" slack="-0"/>
  <constraint name="sendCVIfNonByzAndBlockNotRelayed(1,1,1)" index="2784" slack="1"/>
  <constraint name="sendCVOnlyIfViewBeforeWasAccomplished(1,2)" index="2944" slack="-1.1102230246251565e-15"/>
  <constraint name="nextPrimaryOnlyIfBlockNotRelayed(1,2)" index="2956" slack="0"/>
  <constraint name="calcIfBlockRelayedOnView(1)" index="2968" slack="-0"/>
  <constraint name="calcSumBlockRelayed" index="2972" slack="-0"/>
  <constraint name="calcPrepReqSendEveryNodeAndView(1,1)" index="2973" slack="-0"/>
  <constraint name="calcBlockRelayEveryNodeAndView(1,1)" index="3005" slack="-0"/>
  <constraint name="calcPrepResponseEveryNodeAndView(1,1)" index="3021" slack="-0"/>
  <constraint name="calcChangeViewEveryNodeAndView(1,1)" index="3037" slack="-0"/>
  <constraint name="calcPrepReqEveryNodeAndView(1,1)" index="3053" slack="-0"/>
  <constraint name="calcLastRelayedBlock(1,1,1)" index="3069" slack="40"/>
 </linearConstraints>
 <variables>
  <variable name="totalBlockRelayed" index="0" value="2"/>
  <variable name="SendPrepReq(1,1,1)" index="1" value="0"/>
  <variable name="SendCV(1,1,1)" index="33" value="0"/>
  <variable name="RecvPrepReq(5,2,1,1)" index="49" value="0"/>
  <variable name="RecvPrepReq(4,3,1,1)" index="49" value="0"/>
  <variable name="RecvPrepResp(1,1,1,1)" index="113" value="0"/>
  <variable name="RecvCV(1,1,1,1)" index="177" value="0"/>
  <variable name="BlockRelay(1,1,1)" index="241" value="0"/>
  <variable name="primary(1,1)" index="257" value="0"/>
  <variable name="SendPrepReq(2,1,1)" index="273" value="0"/>
  <variable name="RecvPrepReq(2,1,1,1)" index="417" value="0"/>
  <variable name="BlockRelay(2,1,1)" index="993" value="0"/>
  <variable name="RecvCV(2,1,1,1)" index="1101" value="0"/>
  <variable name="SendPrepResp(2,1,1)" index="1533" value="0"/>
  <variable name="SendPrepResp(8,4,2)" index="1666" value="0"/>
  <variable name="RecvPrepResp(2,1,1,1)" index="1677" value="0"/>
  <variable name="BlockRelay(2,1,4)" index="2253" value="0"/>
  <variable name="SendCV(2,1,1)" index="2289" value="0"/>
  <variable name="RecvCV(2,1,1,4)" index="2433" value="0"/>
  <variable name="blockRelayed(1)" index="2577" value="1"/>
  <variable name="prepReqSendPerNodeAndView(1,1)" index="2581" value="0"/>
  <variable name="blockRelayPerNodeAndView(1,1)" index="2613" value="0"/>
  <variable name="prepRespPerNodeAndView(1,1)" index="2629" value="2"/>
  <variable name="changeViewPerNodeAndView(1,1)" index="2645" value="3"/>
  <variable name="prepReqPerNodeAndView(1,1)" index="2661" value="1"/>
  <variable name="lastRelayedBlock" index="2677" value="-40"/>
 </variables>
</CPLEXSolution>
