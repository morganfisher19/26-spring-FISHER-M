// Visuzlization dimensions

function getChartWidth(): number {
  const screenWidth = window.innerWidth;
  if (screenWidth < 400)  return 250;
  if (screenWidth < 500)  return 350;
  if (screenWidth < 700)  return 400;
  if (screenWidth < 900)  return 600;
  return 800;
}

function getChartHeight(): number {
  const screenWidth = window.innerWidth;
  if (screenWidth < 400)  return 250;
  if (screenWidth < 500)  return 350;
  if (screenWidth < 700)  return 400;
  if (screenWidth < 900)  return 450;
  return 600;
}

function getFontSize(): string {
  const screenWidth = window.innerWidth;
  if (screenWidth < 400)  return '10px';
  if (screenWidth < 500)  return '11px';
  if (screenWidth < 700)  return '12px';
  if (screenWidth < 900)  return '13px';
  return '14px';
}

// type Margin = {
//   top: number;
//   right: number;
//   bottom: number;
//   left: number;
// };

// function getLeftMargin(): number {
//   const screenWidth = window.innerWidth;
//   if (screenWidth < 400)  return 190;
//   if (screenWidth < 500)  return 100;
//   if (screenWidth < 700)  return 150;
//   if (screenWidth < 900)  return 190;
//   return 190;
// }

// function getRightMargin(): number {
//   const screenWidth = window.innerWidth;
//   if (screenWidth < 400)  return 250;
//   if (screenWidth < 500)  return 250;
//   if (screenWidth < 700)  return 250;
//   if (screenWidth < 900)  return 250;
//   return 250;
// }



export const CHART_WIDTH  = getChartWidth();
export const CHART_HEIGHT = getChartHeight();
export const MARGIN = { top: 20, right: 20, bottom: 80, left: 60 };
export const W = CHART_WIDTH  - MARGIN.left - MARGIN.right;
export const H = CHART_HEIGHT - MARGIN.top  - MARGIN.bottom;
export const FONT_SIZE = getFontSize()
// export const LEFT_MARGIN = getLeftMargin()
// export const RIGHT_MARGIN = getRightMargin()
